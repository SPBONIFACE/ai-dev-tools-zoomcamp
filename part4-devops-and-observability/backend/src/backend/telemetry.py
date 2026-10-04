import os
import logging
from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger(__name__)

# Configurable environment settings
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "sdip-backend")
ENVIRONMENT = os.getenv("DEPLOYMENT_ENVIRONMENT", os.getenv("ENVIRONMENT", "local"))
SERVICE_VERSION = os.getenv("SERVICE_VERSION", os.getenv("APP_VERSION", "1.0.0"))
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() in ("true", "1", "yes")

# Resource attributes identifying the service instance
resource = Resource.create({
    "service.name": SERVICE_NAME,
    "service.version": SERVICE_VERSION,
    "deployment.environment.name": ENVIRONMENT,
})

# Tracer and Meter initializers
tracer = trace.get_tracer(SERVICE_NAME, SERVICE_VERSION)
meter = metrics.get_meter(SERVICE_NAME, SERVICE_VERSION)

# Application-specific metrics (as outlined in Part 4)
sessions_created_counter = meter.create_counter(
    name="sdip_sessions_created_total",
    description="Total number of interview sessions created",
    unit="1",
)

active_participants_counter = meter.create_up_down_counter(
    name="sdip_active_participants",
    description="Number of currently active participants in interview sessions",
    unit="1",
)

board_operations_counter = meter.create_counter(
    name="sdip_board_operations_total",
    description="Total number of board operations/elements drawn on canvas",
    unit="1",
)

operation_failures_counter = meter.create_counter(
    name="sdip_operation_failures_total",
    description="Total number of canvas operation and component creation failures",
    unit="1",
)

http_requests_counter = meter.create_counter(
    name="sdip_http_requests_total",
    description="Total HTTP requests processed by endpoint and status",
    unit="1",
)


def setup_telemetry(app=None):
    """Initializes OpenTelemetry tracing, metrics, and auto-instruments FastAPI."""
    if not OTEL_ENABLED:
        logger.info("OpenTelemetry is disabled via OTEL_ENABLED=false")
        return

    # Setup Tracing
    tracer_provider = TracerProvider(resource=resource)
    try:
        otlp_trace_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
    except Exception as e:
        logger.warning(f"Could not connect to OTLP trace exporter at {OTLP_ENDPOINT}: {e}. Falling back to console.")
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    
    trace.set_tracer_provider(tracer_provider)

    # Setup Metrics
    try:
        otlp_metric_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
        metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)
    except Exception as e:
        logger.warning(f"Could not connect to OTLP metric exporter at {OTLP_ENDPOINT}: {e}. Falling back to console.")
        metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=15000)

    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Auto-instrument FastAPI if application is provided
    if app:
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            excluded_urls="api/health,docs,openapi.json,redoc",
        )
        logger.info(f"OpenTelemetry instrumentation initialized for {SERVICE_NAME} ({ENVIRONMENT}, v{SERVICE_VERSION})")
