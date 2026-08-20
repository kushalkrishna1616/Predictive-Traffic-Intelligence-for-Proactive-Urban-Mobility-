"""
FastAPI & Uvicorn High-Performance Server
Problem Statement: AI/ML-09 / AML-05 (Innohack Project)

Asynchronous non-blocking web server powered by FastAPI & Uvicorn.
Serves OpenCV CCTV live video frames, simulation engine, XAI breakdowns,
and glassmorphic dashboard UI with zero socket blocking.
"""

import os
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, Response, Request, Body
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

import bmd45_pipeline
import iot_simulator
import predictor
import route_optimizer
import cctv_video_processor
import scenario_simulator

app = FastAPI(title="RoutePulse AI Engine & Command Center", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core AI Modules
pipe = bmd45_pipeline.BMD45Pipeline()
sim = iot_simulator.IoTSimulator()
pred = predictor.TrafficPredictor()
opt = route_optimizer.RouteOptimizer()
video_proc = cctv_video_processor.CCTVVideoProcessor()
scenario = scenario_simulator.ScenarioSimulator()

current_simulation_state = scenario.simulate_scenario()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_V1 = os.path.join(PROJECT_ROOT, "traffic_dashboard.html")
HTML_V2 = os.path.join(PROJECT_ROOT, "traffic_dashboard_v2.html")

# Static Dashboard UI Routes
@app.get("/")
async def serve_root():
    return FileResponse(HTML_V2)

@app.get("/v2")
@app.get("/v2.html")
@app.get("/traffic_dashboard_v2.html")
async def serve_v2():
    return FileResponse(HTML_V2)

@app.get("/traffic_dashboard.html")
async def serve_v1():
    return FileResponse(HTML_V1)

# Live OpenCV CCTV Video Stream & Frame Endpoints
@app.get("/api/video/frame")
async def get_video_frame():
    frame_data = video_proc.process_next_frame()
    return Response(content=frame_data["jpeg_bytes"], media_type="image/jpeg")

@app.get("/api/video/telemetry")
async def get_video_telemetry():
    frame_data = video_proc.process_next_frame()
    telemetry = {k: v for k, v in frame_data.items() if k != "jpeg_bytes"}
    return telemetry

# Scenario Simulator & Explainable AI Endpoints
@app.get("/api/simulation/current")
async def get_current_simulation():
    return current_simulation_state

@app.post("/api/simulation/apply")
async def apply_simulation(payload: Dict[str, Any] = Body(...)):
    global current_simulation_state
    vol_mult = float(payload.get("volume_multiplier", 1.0))
    rain = bool(payload.get("rain_active", False))
    accident = payload.get("accident_corridor", None)
    closure = bool(payload.get("lane_closure_active", False))

    current_simulation_state = scenario.simulate_scenario(vol_mult, rain, accident, closure)
    return current_simulation_state

@app.get("/api/traffic/explain")
async def get_xai_explain():
    return {
        "corridor": "Silk Board Junction",
        "xai_breakdown": current_simulation_state.get("xai_breakdown", [])
    }

@app.get("/api/incidents/active")
async def get_active_incidents():
    return {
        "active_incidents_count": current_simulation_state.get("summary", {}).get("active_incidents_count", 0),
        "incidents": current_simulation_state.get("incidents", [])
    }

@app.get("/api/datasets/available")
async def get_available_datasets():
    return {
        "datasets": [
            {"id": "bmd45", "name": "IISc BMD-45 Bengaluru Mobility Vision Dataset", "type": "Real-world CCTV 14-Vehicle Classes", "status": "ACTIVE"},
            {"id": "metr_la", "name": "METR-LA Highway Traffic Sensor Time-Series", "type": "Loop Detector Speed Telemetry", "status": "READY"},
            {"id": "ua_detrac", "name": "UA-DETRAC Real Traffic Video Dataset", "type": "CCTV Bounding Boxes & Optical Tracking", "status": "READY"},
            {"id": "bengaluru_graph", "name": "Bengaluru Arterial OpenStreetMap Graph", "type": "Geospatial Road Network", "status": "ACTIVE"}
        ]
    }

# General API Telemetry & Optimization Routes
@app.get("/api/info")
@app.get("/api")
async def get_api_info():
    return {
        "status": "ONLINE",
        "server": "FastAPI + Uvicorn High-Performance Server",
        "system": "Traffic Congestion AI Engine (AI/ML-09)",
        "endpoints": ["/api/video/frame", "/api/video/telemetry", "/api/traffic/live", "/api/traffic/predict", "/api/simulation/current", "/api/route/optimize"]
    }

@app.get("/api/traffic/live")
async def get_live_traffic():
    frame_data = video_proc.process_next_frame()
    video_telemetry = {k: v for k, v in frame_data.items() if k != "jpeg_bytes"}

    telemetry = sim.get_live_telemetry()
    telemetry[0]["congestion_pct"] = video_telemetry["congestion_pct"]
    telemetry[0]["current_speed_kmh"] = video_telemetry["avg_speed_kmh"]
    telemetry[0]["delay_min"] = video_telemetry["delay_min"]
    telemetry[0]["status"] = video_telemetry["status"]
    telemetry[0]["status_color"] = video_telemetry["status_color"]

    return {
        "corridors_count": len(telemetry),
        "video_analytics": video_telemetry,
        "telemetry": telemetry
    }

@app.get("/api/traffic/predict")
async def get_traffic_predict():
    telemetry = sim.get_live_telemetry()
    return pred.get_citywide_forecast(telemetry)

@app.get("/api/route/optimize")
async def get_route_optimize(route_id: Optional[str] = None):
    return opt.calculate_optimized_route(route_id)

@app.post("/api/emergency/greenwave")
async def trigger_emergency_greenwave(payload: Dict[str, Any] = Body(...)):
    corridor = payload.get("corridor", "Silk Board Junction")
    hospital = payload.get("hospital_name", "St. John's Hospital (Koramangala)")
    return opt.activate_emergency_green_wave(corridor, hospital)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False, workers=2)
