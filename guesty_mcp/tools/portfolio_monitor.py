"""Portfolio monitoring tool for Guesty property management."""

from mcp.server.fastmcp import Context
from typing import List, Optional, Dict, Any
from pydantic import Field
from typing_extensions import Annotated
from datetime import datetime, timedelta
import logging

from ..auth import extract_guesty_credentials_from_headers
from ..client import GuestyAPIClient

logger = logging.getLogger(__name__)


async def guesty_monitor_portfolio_impl(
    ctx: Context,
    property_ids: Annotated[Optional[List[str]], Field(description="Specific properties to monitor, or all if not specified")] = None,
    include_alerts: Annotated[bool, Field(description="Include urgent issues requiring attention")] = True,
    performance_metrics: Annotated[bool, Field(description="Include occupancy rates, revenue, and booking trends")] = True
) -> Dict[str, Any]:
    """
    Monitor property portfolio performance, occupancy, and operational status.
    
    Provides a real-time dashboard view of all properties with key metrics,
    upcoming reservations, pending tasks, and urgent alerts requiring attention.
    """
    logger.info("🏨 Starting portfolio monitoring")
    
    # Extract credentials
    credentials = extract_guesty_credentials_from_headers(ctx)
    client = GuestyAPIClient(credentials['client_id'], credentials['client_secret'])
    
    try:
        # Get all listings if no specific properties specified
        if not property_ids:
            logger.info("📋 Fetching all properties")
            listings_response = await client.get("/listings")
            properties = listings_response.get("results", [])
            property_ids = [prop["_id"] for prop in properties]
        else:
            properties = []
            for prop_id in property_ids:
                prop_response = await client.get(f"/listings/{prop_id}")
                properties.append(prop_response)
        
        logger.info(f"📊 Analyzing {len(properties)} properties")
        
        # Get reservations for next 30 days
        end_date = datetime.now() + timedelta(days=30)
        reservations_params = {
            "checkInDateFrom": datetime.now().strftime("%Y-%m-%d"),
            "checkInDateTo": end_date.strftime("%Y-%m-%d"),
            "listingIds": ",".join(property_ids)
        }
        reservations_response = await client.get("/reservations", params=reservations_params)
        reservations = reservations_response.get("results", [])
        
        # Get tasks for all properties
        tasks_params = {"listingIds": ",".join(property_ids)}
        tasks_response = await client.get("/tasks", params=tasks_params)
        tasks = tasks_response.get("results", [])
        
        # Process data into portfolio dashboard
        portfolio_summary = {
            "total_properties": len(properties),
            "current_occupancy_rate": 0,
            "upcoming_checkins": 0,
            "upcoming_checkouts": 0,
            "revenue_this_month": 0,
            "pending_tasks": len([t for t in tasks if t.get("status") == "pending"])
        }
        
        property_status = []
        alerts = []
        
        # Process each property
        for prop in properties:
            prop_id = prop["_id"]
            prop_name = prop.get("title", "Unnamed Property")
            
            # Get property reservations
            prop_reservations = [r for r in reservations if r.get("listing", {}).get("_id") == prop_id]
            
            # Calculate status
            current_reservation = None
            for res in prop_reservations:
                checkin = datetime.fromisoformat(res["checkIn"].replace("Z", "+00:00"))
                checkout = datetime.fromisoformat(res["checkOut"].replace("Z", "+00:00"))
                now = datetime.now()
                
                if checkin <= now <= checkout:
                    current_reservation = res
                    break
            
            status = "occupied" if current_reservation else "vacant"
            
            # Find next reservation
            future_reservations = [
                r for r in prop_reservations 
                if datetime.fromisoformat(r["checkIn"].replace("Z", "+00:00")) > datetime.now()
            ]
            next_reservation = min(future_reservations, key=lambda x: x["checkIn"]) if future_reservations else None
            
            # Get property tasks
            prop_tasks = [t for t in tasks if t.get("listing", {}).get("_id") == prop_id]
            urgent_tasks = [t for t in prop_tasks if t.get("priority") == "high" and t.get("status") == "pending"]
            
            # Add to portfolio status
            property_status.append({
                "property_id": prop_id,
                "property_name": prop_name,
                "current_status": status,
                "current_guest": current_reservation.get("guest", {}).get("fullName") if current_reservation else None,
                "next_reservation": {
                    "guest_name": next_reservation.get("guest", {}).get("fullName"),
                    "checkin_date": next_reservation.get("checkIn"),
                    "nights": next_reservation.get("nights")
                } if next_reservation else None,
                "urgent_issues": len(urgent_tasks),
                "pending_tasks": len([t for t in prop_tasks if t.get("status") == "pending"])
            })
            
            # Add alerts for urgent issues
            if urgent_tasks:
                alerts.append({
                    "property_name": prop_name,
                    "type": "urgent_tasks",
                    "count": len(urgent_tasks),
                    "message": f"{len(urgent_tasks)} urgent tasks pending"
                })
        
        # Calculate summary metrics
        if performance_metrics:
            occupied_properties = len([p for p in property_status if p["current_status"] == "occupied"])
            portfolio_summary["current_occupancy_rate"] = (occupied_properties / len(properties) * 100) if properties else 0
            
            # Count upcoming checkins/checkouts in next 7 days
            week_from_now = datetime.now() + timedelta(days=7)
            portfolio_summary["upcoming_checkins"] = len([
                r for r in reservations 
                if datetime.now() <= datetime.fromisoformat(r["checkIn"].replace("Z", "+00:00")) <= week_from_now
            ])
            portfolio_summary["upcoming_checkouts"] = len([
                r for r in reservations 
                if datetime.now() <= datetime.fromisoformat(r["checkOut"].replace("Z", "+00:00")) <= week_from_now
            ])
        
        result = {
            "portfolio_summary": portfolio_summary,
            "property_status": property_status,
            "alerts": alerts if include_alerts else [],
            "total_properties_analyzed": len(properties),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✓ Portfolio monitoring completed - {len(properties)} properties analyzed")
        return result
        
    except Exception as e:
        logger.error(f"✗ Portfolio monitoring failed: {str(e)}")
        raise Exception(f"Failed to monitor portfolio: {str(e)}")
    finally:
        await client.aclose()