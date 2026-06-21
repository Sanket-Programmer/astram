# import streamlit as st
# import pandas as pd
# import numpy as np
# import joblib
# import os
# import folium
# from folium.plugins import HeatMap
# from streamlit_folium import st_folium
# import streamlit.components.v1 as components
# import plotly.express as px

# # ============================================================
# # PAGE CONFIG
# # ============================================================

# st.set_page_config(
#     page_title="ASTraM Command Center",
#     page_icon="🚦",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.title("ASTraM Command Center")
# st.markdown(
#     """
#     **AI-Driven Event Impact Forecasting & Resource Deployment for Bengaluru Traffic Police**  
#     """
# )

# # ============================================================
# # LOAD DATA
# # ============================================================

# @st.cache_data
# def load_data():
#     df = pd.read_csv("impact_dataset.csv")

#     # safe numeric conversion
#     for col in ["latitude", "longitude", "impact_score"]:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors="coerce")

#     # fill common nulls used in app
#     for col in ["event_cause", "priority", "event_type", "police_station", "zone", "junction"]:
#         if col in df.columns:
#             df[col] = df[col].fillna("Unknown").astype(str).str.strip()

#     # standardize casing for priority / event_type
#     if "priority" in df.columns:
#         df["priority"] = df["priority"].replace({
#             "high": "High",
#             "low": "Low"
#         })

#     if "event_type" in df.columns:
#         df["event_type"] = df["event_type"].str.lower()

#     return df


# @st.cache_resource
# def load_model():
#     model_path = "traffic_impact_predictor.pkl"
#     if os.path.exists(model_path):
#         model = joblib.load(model_path)
#         return model, True
#     else:
#         return None, False


# df = load_data()
# model, model_loaded = load_model()

# if not model_loaded:
#     st.error("⚠️ Model file `traffic_impact_predictor.pkl` not found in the project folder.")
#     st.stop()

# # ============================================================
# # UTILITY FUNCTIONS
# # ============================================================

# def get_risk(impact):
#     if impact >= 75:
#         return "HIGH"
#     elif impact >= 55:
#         return "MEDIUM"
#     else:
#         return "LOW"


# def get_pin_color(risk):
#     if risk == "HIGH":
#         return "red"
#     elif risk == "MEDIUM":
#         return "orange"
#     else:
#         return "green"


# def get_operational_radius(risk):
#     if risk == "HIGH":
#         return 2500
#     elif risk == "MEDIUM":
#         return 1500
#     else:
#         return 700


# def get_event_cause_score(event_cause):
#     """
#     Severity score for each event cause (0-100).
#     Higher score => higher operational load.
#     """
#     severity_map = {
#         "accident": 90,
#         "public_event": 85,
#         "procession": 82,
#         "protest": 85,
#         "construction": 75,
#         "water_logging": 78,
#         "vehicle_breakdown": 60,
#         "congestion": 70,
#         "tree_fall": 72,
#         "pot_holes": 45,
#         "road_conditions": 50,
#         "others": 55,
#         "debris": 58,
#         "fog_low_visibility": 62,
#         "vip_movement": 88,
#         "test_demo": 65
#     }
#     return severity_map.get(str(event_cause).strip(), 55)


# def get_priority_score(priority):
#     return 100 if str(priority).strip().lower() == "high" else 40


# def get_closure_score(requires_road_closure):
#     return 100 if requires_road_closure else 20


# def get_event_type_score(event_type):
#     """
#     Planned events usually require more barricading/diversion prep.
#     """
#     return 65 if str(event_type).strip().lower() == "planned" else 50


# def get_hotspot_score(hotspot_event_count=None, hotspot_avg_impact=None):
#     """
#     Convert historical hotspot intensity into a 0-100 scale.
#     """
#     if hotspot_event_count is None and hotspot_avg_impact is None:
#         return 40

#     event_component = 0
#     impact_component = 0

#     if hotspot_event_count is not None:
#         event_component = min((hotspot_event_count / 60) * 100, 100)

#     if hotspot_avg_impact is not None:
#         impact_component = min(hotspot_avg_impact, 100)

#     if hotspot_event_count is not None and hotspot_avg_impact is not None:
#         return round((event_component * 0.45) + (impact_component * 0.55), 2)
#     elif hotspot_avg_impact is not None:
#         return round(impact_component, 2)
#     else:
#         return round(event_component, 2)


# def get_diversion_plan(impact, requires_road_closure, event_cause, rns):
#     """
#     Decide whether diversion is required and provide a simple operational plan.
#     """
#     high_diversion_causes = {
#         "public_event", "procession", "protest",
#         "construction", "water_logging", "vip_movement"
#     }

#     if requires_road_closure or rns >= 85:
#         return {
#             "diversion_required": "YES",
#             "diversion_level": "CORRIDOR",
#             "diversion_plan": "Activate corridor-level diversion and upstream traffic advisory 1-2 km before the incident."
#         }

#     if event_cause in high_diversion_causes and impact >= 65:
#         return {
#             "diversion_required": "YES",
#             "diversion_level": "JUNCTION",
#             "diversion_plan": "Implement junction-level diversion and pre-position barricades on feeder roads."
#         }

#     if event_cause in {"public_event", "procession", "protest", "construction", "vip_movement"} and impact >= 55:
#         return {
#             "diversion_required": "MAYBE",
#             "diversion_level": "LOCAL",
#             "diversion_plan": "Prepare a preventive diversion advisory and stage barricades at nearby feeder routes."
#         }

#     if impact >= 55 or rns >= 65:
#         return {
#             "diversion_required": "MAYBE",
#             "diversion_level": "LOCAL",
#             "diversion_plan": "Keep local alternate route advisory ready and divert traffic if queue builds."
#         }

#     return {
#         "diversion_required": "NO",
#         "diversion_level": "NONE",
#         "diversion_plan": "No diversion required. Maintain routine monitoring."
#     }


# def compute_resource_need_score(
#     impact,
#     event_cause,
#     priority,
#     requires_road_closure,
#     event_type,
#     hotspot_event_count=None,
#     hotspot_avg_impact=None
# ):
#     """
#     Weighted operational resource score.
#     """
#     priority_score = get_priority_score(priority)
#     closure_score = get_closure_score(requires_road_closure)
#     cause_score = get_event_cause_score(event_cause)
#     event_type_score = get_event_type_score(event_type)
#     hotspot_score = get_hotspot_score(hotspot_event_count, hotspot_avg_impact)

#     rns = (
#         impact * 0.40 +
#         priority_score * 0.15 +
#         closure_score * 0.15 +
#         cause_score * 0.15 +
#         event_type_score * 0.05 +
#         hotspot_score * 0.10
#     )

#     return round(rns, 2)


# def recommend_resources(
#     impact,
#     requires_road_closure=False,
#     event_cause="others",
#     priority="Low",
#     event_type="unplanned",
#     hotspot_event_count=None,
#     hotspot_avg_impact=None
# ):
#     """
#     Balanced advanced resource recommendation engine.
#     Keeps the same output keys used across the dashboard.
#     """

#     # ------------------------------------------------------------
#     # 1) Resource Need Score
#     # ------------------------------------------------------------
#     rns = compute_resource_need_score(
#         impact=impact,
#         event_cause=event_cause,
#         priority=priority,
#         requires_road_closure=requires_road_closure,
#         event_type=event_type,
#         hotspot_event_count=hotspot_event_count,
#         hotspot_avg_impact=hotspot_avg_impact
#     )

#     # ------------------------------------------------------------
#     # 2) Base allocation from RNS (flatter scaling)
#     # ------------------------------------------------------------
#     if rns < 45:
#         risk = "LOW"
#         officers = 2
#         barricades = 1
#         resource_category = "LOW"

#     elif rns < 60:
#         risk = "LOW"
#         officers = 3
#         barricades = 2
#         resource_category = "LOW"

#     elif rns < 75:
#         risk = "MEDIUM"
#         officers = 4
#         barricades = 4
#         resource_category = "MEDIUM"

#     elif rns < 90:
#         risk = "HIGH"
#         officers = 5
#         barricades = 5
#         resource_category = "HIGH"

#     else:
#         risk = "HIGH"
#         officers = 6
#         barricades = 7
#         resource_category = "HIGH"

#     # ------------------------------------------------------------
#     # 3) Controlled event-specific adjustments
#     # ------------------------------------------------------------
#     officer_adj = 0
#     barricade_adj = 0

#     if event_cause == "accident":
#         officer_adj += 1
#         barricade_adj += 1

#     elif event_cause in ["public_event", "procession", "protest", "vip_movement"]:
#         officer_adj += 1
#         barricade_adj += 2

#     elif event_cause in ["construction", "water_logging", "tree_fall"]:
#         barricade_adj += 2

#     elif event_cause == "vehicle_breakdown":
#         officer_adj += 1
#         if impact >= 70:
#             barricade_adj += 1

#     elif event_cause == "congestion":
#         officer_adj += 1

#     # ------------------------------------------------------------
#     # 4) Priority adjustment
#     # ------------------------------------------------------------
#     if str(priority).strip().lower() == "high":
#         officer_adj += 1

#     # ------------------------------------------------------------
#     # 5) Road closure adjustment
#     # ------------------------------------------------------------
#     if requires_road_closure:
#         officer_adj += 1
#         barricade_adj += 1

#     # ------------------------------------------------------------
#     # 6) Planned vs unplanned adjustment
#     # ------------------------------------------------------------
#     if str(event_type).strip().lower() == "planned":
#         barricade_adj += 1

#         if event_cause in ["public_event", "procession", "protest", "construction", "vip_movement"]:
#             barricade_adj += 1

#     else:
#         if event_cause in ["accident", "vehicle_breakdown", "tree_fall", "water_logging", "congestion"]:
#             officer_adj += 1

#     # ------------------------------------------------------------
#     # 7) Hotspot adjustment
#     # ------------------------------------------------------------
#     hotspot_score = get_hotspot_score(hotspot_event_count, hotspot_avg_impact)
#     if hotspot_score >= 75:
#         barricade_adj += 1
#     elif hotspot_score >= 60 and risk != "LOW":
#         barricade_adj += 1

#     # ------------------------------------------------------------
#     # 8) Cap adjustments so counts don't spike too aggressively
#     # ------------------------------------------------------------
#     officer_adj = min(officer_adj, 3)
#     barricade_adj = min(barricade_adj, 4)

#     officers += officer_adj
#     barricades += barricade_adj

#     # ------------------------------------------------------------
#     # 9) Soft caps by risk band
#     # ------------------------------------------------------------
#     if risk == "LOW":
#         officers = min(officers, 4)
#         barricades = min(barricades, 4)

#     elif risk == "MEDIUM":
#         officers = min(officers, 6)
#         barricades = min(barricades, 6)

#     else:
#         officers = min(officers, 8)
#         barricades = min(barricades, 9)

#     # ------------------------------------------------------------
#     # 10) Diversion logic
#     # ------------------------------------------------------------
#     diversion_info = get_diversion_plan(
#         impact=impact,
#         requires_road_closure=requires_road_closure,
#         event_cause=event_cause,
#         rns=rns
#     )

#     # ------------------------------------------------------------
#     # 11) Recommended actions
#     # ------------------------------------------------------------
#     actions = []

#     if risk == "HIGH":
#         actions.append("Deploy Traffic Response Team immediately")
#     elif risk == "MEDIUM":
#         actions.append("Deploy additional traffic personnel")
#     else:
#         actions.append("Routine monitoring")

#     if barricades >= 5:
#         actions.append("Install temporary barricades at approach roads")
#     else:
#         actions.append("Place temporary barricades near congestion points")

#     if diversion_info["diversion_required"] == "YES":
#         actions.append("Activate diversion route and public traffic advisory")
#     elif diversion_info["diversion_required"] == "MAYBE":
#         actions.append("Keep alternate route advisory ready; divert if queue builds")
#     else:
#         actions.append("No diversion required")

#     if risk == "HIGH":
#         actions.append("Continuous live monitoring until clearance")
#     elif risk == "MEDIUM":
#         actions.append("Coordinate with nearest police station")
#     else:
#         actions.append("Keep response team on low alert")

#     return {
#         "risk": risk,
#         "officers": officers,
#         "barricades": barricades,
#         "resource_category": resource_category,
#         "diversion_required": diversion_info["diversion_required"],
#         "diversion": diversion_info["diversion_plan"],
#         "actions": actions[:4]
#     }


# def build_hotspot_table(data):
#     """
#     Build top hotspot table from junction-level aggregation.
#     """
#     hotspot_df = (
#         data[data["junction"].notna()]
#         .groupby("junction")
#         .agg(
#             event_count=("id", "count"),
#             avg_impact=("impact_score", "mean"),
#             latitude=("latitude", "mean"),
#             longitude=("longitude", "mean")
#         )
#         .reset_index()
#         .sort_values(by=["event_count", "avg_impact"], ascending=False)
#     )

#     hotspot_df["risk_level"] = hotspot_df["avg_impact"].apply(get_risk)
#     return hotspot_df


# def save_feedback_log(feedback_dict, log_file="astram_retraining_log.csv"):
#     """
#     Save post-event feedback to CSV.
#     """
#     feedback_df = pd.DataFrame([feedback_dict])
#     abs_path = os.path.abspath(log_file)

#     if os.path.exists(abs_path):
#         old_df = pd.read_csv(abs_path)
#         updated_df = pd.concat([old_df, feedback_df], ignore_index=True)
#         updated_df.to_csv(abs_path, index=False)
#     else:
#         feedback_df.to_csv(abs_path, index=False)

#     return abs_path


# def get_filtered_junctions(data, selected_zone="Unknown", selected_station="Unknown"):
#     """
#     Return junction list filtered by zone/police station.
#     """
#     temp = data.copy()

#     if selected_zone != "Unknown" and "zone" in temp.columns:
#         temp = temp[temp["zone"] == selected_zone]

#     if selected_station != "Unknown" and "police_station" in temp.columns:
#         temp = temp[temp["police_station"] == selected_station]

#     junctions = sorted(
#         temp["junction"]
#         .dropna()
#         .astype(str)
#         .str.strip()
#         .unique()
#         .tolist()
#     )

#     if len(junctions) == 0:
#         return ["Unknown"]

#     return junctions


# hotspots = build_hotspot_table(df)

# # ============================================================
# # SIDEBAR NAVIGATION
# # ============================================================

# st.sidebar.title("Navigation")

# page = st.sidebar.radio(
#     "Select Module",
#     [
#         "Dashboard Overview",
#         "Forecasting Command Center",
#         "Hotspot Intelligence",
#         "Event Analytics"
#     ]
# )

# # ============================================================
# # PAGE 1: DASHBOARD OVERVIEW
# # ============================================================

# if page == "Dashboard Overview":

#     st.subheader("Citywide Traffic Event Overview")

#     total_events = len(df)
#     planned_events = (df["event_type"] == "planned").sum()
#     unplanned_events = (df["event_type"] == "unplanned").sum()
#     high_priority_events = (df["priority"].str.lower() == "high").sum()
#     avg_impact = df["impact_score"].mean()

#     c1, c2, c3, c4, c5 = st.columns(5)
#     c1.metric("Total Events", total_events)
#     c2.metric("Planned Events", planned_events)
#     c3.metric("Unplanned Events", unplanned_events)
#     c4.metric("High Priority Events", high_priority_events)
#     c5.metric("Avg Traffic Impact Index", f"{avg_impact:.2f}")

#     st.markdown("---")

#     left, right = st.columns(2)

#     with left:
#         st.subheader("Top Event Causes")
#         cause_counts = (
#             df["event_cause"]
#             .value_counts()
#             .reset_index()
#         )
#         cause_counts.columns = ["Event Cause", "Count"]

#         fig1 = px.bar(
#             cause_counts.head(10),
#             x="Event Cause",
#             y="Count",
#             title="Top Event Causes"
#         )
#         st.plotly_chart(fig1, use_container_width=True)

#     with right:
#         st.subheader("Priority Distribution")
#         priority_counts = (
#             df["priority"]
#             .value_counts()
#             .reset_index()
#         )
#         priority_counts.columns = ["Priority", "Count"]

#         fig2 = px.pie(
#             priority_counts,
#             names="Priority",
#             values="Count",
#             title="Priority Distribution"
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     st.markdown("---")

#     st.subheader("Top Junction Hotspots")

#     hotspot_preview = hotspots[
#         ["junction", "event_count", "avg_impact", "risk_level"]
#     ].head(10).copy()

#     hotspot_preview.columns = [
#         "Junction",
#         "Events",
#         "Traffic Impact Index",
#         "Risk Level"
#     ]

#     st.dataframe(hotspot_preview, use_container_width=True)

#     st.info(
#         """
#         **What this system does**
#         - Forecasts event-related traffic impact from historical incident patterns
#         - Identifies recurring congestion hotspots
#         - Recommends officers, barricades, and whether diversion is required
#         - Supports post-event learning for future model improvement
#         """
#     )

# # ============================================================
# # PAGE 2: FORECASTING COMMAND CENTER
# # ============================================================

# elif page == "Forecasting Command Center":

#     st.subheader("🚨 Incident Forecasting & Resource Deployment")

#     st.sidebar.header("Incident Input")

#     # Sidebar Inputs
#     event_cause_options = sorted(df["event_cause"].dropna().unique().tolist())
#     event_type_options = sorted(df["event_type"].dropna().unique().tolist())
#     priority_options = ["High", "Low"]

#     event_cause = st.sidebar.selectbox("Event Cause", event_cause_options)
#     event_type = st.sidebar.selectbox("Event Type", event_type_options)
#     priority = st.sidebar.selectbox("Priority", priority_options)

#     requires_road_closure = st.sidebar.radio(
#         "Requires Road Closure?",
#         [True, False],
#         horizontal=True
#     )

#     # Optional operational context
#     st.sidebar.divider()
#     st.sidebar.subheader("📍 Operational Context")

#     zone_options = ["Unknown"] + sorted(
#         [z for z in df["zone"].dropna().unique().tolist() if z != "Unknown"]
#     ) if "zone" in df.columns else ["Unknown"]

#     police_options = ["Unknown"] + sorted(
#         [p for p in df["police_station"].dropna().unique().tolist() if p != "Unknown"]
#     ) if "police_station" in df.columns else ["Unknown"]

#     selected_zone = st.sidebar.selectbox("Zone", zone_options)
#     selected_station = st.sidebar.selectbox("Police Station", police_options)

#     # NEW: Junction input required for the new model
#     junction_options = get_filtered_junctions(df, selected_zone, selected_station)
#     selected_junction = st.sidebar.selectbox("Junction", junction_options)

#     description_input = st.sidebar.text_area(
#         "Incident Notes (optional)",
#         placeholder="e.g. heavy vehicle breakdown near junction causing lane blockage"
#     )

#     st.sidebar.divider()
#     show_hotspots = st.sidebar.checkbox("Overlay Historical Hotspots", value=True)

#     analyze_btn = st.sidebar.button("🚨 Analyze Incident", use_container_width=True)

#     if analyze_btn:

#         # ========================================================
#         # MODEL INPUT (UPDATED FOR NEW 5-FEATURE MODEL)
#         # ========================================================
#         input_df = pd.DataFrame({
#             "event_cause": [event_cause],
#             "priority": [priority],
#             "requires_road_closure": [requires_road_closure],
#             "event_type": [event_type],
#             "junction": [selected_junction]
#         })

#         predicted_impact = float(model.predict(input_df)[0])
#         predicted_risk = get_risk(predicted_impact)

#         # ========================================================
#         # FILTER HISTORICAL DATA AROUND THE SELECTED CONTEXT
#         # ========================================================
#         filtered_df = df.copy()

#         # प्राथमिक filter = selected junction if available
#         if selected_junction != "Unknown" and "junction" in filtered_df.columns:
#             temp = filtered_df[filtered_df["junction"] == selected_junction]
#             if len(temp) > 0:
#                 filtered_df = temp
#             else:
#                 # fallback to event cause + context
#                 filtered_df = df[df["event_cause"] == event_cause].copy()
#         else:
#             filtered_df = df[df["event_cause"] == event_cause].copy()

#         if selected_zone != "Unknown" and "zone" in filtered_df.columns:
#             temp = filtered_df[filtered_df["zone"] == selected_zone]
#             if len(temp) > 0:
#                 filtered_df = temp

#         if selected_station != "Unknown" and "police_station" in filtered_df.columns:
#             temp = filtered_df[filtered_df["police_station"] == selected_station]
#             if len(temp) > 0:
#                 filtered_df = temp

#         # ========================================================
#         # MAP LOCATION SELECTION
#         # ========================================================
#         if len(filtered_df) > 0 and filtered_df["latitude"].notna().sum() > 0:
#             selected_lat = filtered_df["latitude"].dropna().mean()
#             selected_lon = filtered_df["longitude"].dropna().mean()
#         else:
#             selected_lat = df["latitude"].dropna().mean()
#             selected_lon = df["longitude"].dropna().mean()

#         selected_coords = [selected_lat, selected_lon]

#         # ========================================================
#         # RELATED HOTSPOT (UPDATED TO USE JUNCTION FIRST)
#         # ========================================================
#         related_hotspot = None

#         if selected_junction != "Unknown":
#             temp_hotspot = hotspots[hotspots["junction"] == selected_junction]
#             if len(temp_hotspot) > 0:
#                 related_hotspot = temp_hotspot.head(1)

#         if related_hotspot is None and "junction" in filtered_df.columns and filtered_df["junction"].notna().sum() > 0:
#             related_hotspot = (
#                 filtered_df[filtered_df["junction"].notna()]
#                 .groupby("junction")
#                 .agg(
#                     event_count=("id", "count"),
#                     avg_impact=("impact_score", "mean")
#                 )
#                 .reset_index()
#                 .sort_values(by=["event_count", "avg_impact"], ascending=False)
#                 .head(1)
#             )

#         # ========================================================
#         # ADVANCED RESOURCE ALLOCATION
#         # ========================================================
#         hotspot_event_count = None
#         hotspot_avg_impact = None

#         if related_hotspot is not None and len(related_hotspot) > 0:
#             hotspot_event_count = int(related_hotspot.iloc[0]["event_count"])
#             hotspot_avg_impact = float(related_hotspot.iloc[0]["avg_impact"])

#         rec = recommend_resources(
#             impact=predicted_impact,
#             requires_road_closure=requires_road_closure,
#             event_cause=event_cause,
#             priority=priority,
#             event_type=event_type,
#             hotspot_event_count=hotspot_event_count,
#             hotspot_avg_impact=hotspot_avg_impact
#         )

#         # ========================================================
#         # MAIN ALERT BANNER
#         # ========================================================
#         if predicted_risk == "HIGH":
#             st.error(f"🚨 HIGH IMPACT ALERT: Predicted Traffic Impact Index = {predicted_impact:.2f}")
#         elif predicted_risk == "MEDIUM":
#             st.warning(f"⚠️ MEDIUM IMPACT ALERT: Predicted Traffic Impact Index = {predicted_impact:.2f}")
#         else:
#             st.success(f"✅ LOW IMPACT ALERT: Predicted Traffic Impact Index = {predicted_impact:.2f}")

#         # ========================================================
#         # KPI CARDS
#         # ========================================================
#         col1, col2, col3, col4, col5 = st.columns(5)
#         col1.metric("Traffic Impact Index", f"{predicted_impact:.2f}")
#         col2.metric("Risk Level", rec["risk"])
#         col3.metric("Recommended Officers", rec["officers"])
#         col4.metric("Barricades", rec["barricades"])
#         col5.metric("Diversion Required", rec["diversion_required"])

#         tab1, tab2, tab3 = st.tabs(
#             ["Tactical Map", "AI Reasoning & Dispatch", "Post-Event Learning Loop"]
#         )

#         # ========================================================
#         # TAB 1: TACTICAL MAP
#         # ========================================================
#         with tab1:
#             st.subheader("Tactical Map")

#             m = folium.Map(
#                 location=selected_coords,
#                 zoom_start=12,
#                 tiles="CartoDB dark_matter"
#             )

#             # Historical hotspot overlay
#             if show_hotspots:
#                 heat_df = df.dropna(subset=["latitude", "longitude", "impact_score"]).copy()
#                 heat_data = heat_df[["latitude", "longitude", "impact_score"]].values.tolist()

#                 HeatMap(
#                     heat_data,
#                     radius=15,
#                     blur=12,
#                     max_zoom=13
#                 ).add_to(m)

#             popup_text = f"""
#             <b>Forecasted Incident</b><br>
#             Event Cause: {event_cause}<br>
#             Event Type: {event_type}<br>
#             Priority: {priority}<br>
#             Junction: {selected_junction}<br>
#             Requires Closure: {requires_road_closure}<br>
#             Predicted TII: {predicted_impact:.2f}<br>
#             Risk Level: {predicted_risk}<br>
#             Officers: {rec['officers']}<br>
#             Barricades: {rec['barricades']}<br>
#             Diversion Required: {rec['diversion_required']}<br>
#             Diversion Plan: {rec['diversion']}
#             """

#             folium.Marker(
#                 location=selected_coords,
#                 popup=popup_text,
#                 tooltip="Forecasted Incident",
#                 icon=folium.Icon(color=get_pin_color(predicted_risk), icon="info-sign")
#             ).add_to(m)

#             radius = get_operational_radius(predicted_risk)

#             folium.Circle(
#                 location=selected_coords,
#                 radius=radius,
#                 color=get_pin_color(predicted_risk),
#                 fill=True,
#                 fill_opacity=0.35
#             ).add_to(m)

#             if related_hotspot is not None and len(related_hotspot) > 0:
#                 hotspot_name = related_hotspot.iloc[0]["junction"]
#                 hotspot_events = related_hotspot.iloc[0]["event_count"]
#                 hotspot_impact = related_hotspot.iloc[0]["avg_impact"]

#                 st.info(
#                     f"**Closest historical pattern:** {hotspot_name} "
#                     f"(Events: {hotspot_events}, Avg TII: {hotspot_impact:.2f})"
#                 )

#             st_folium(m, width=1200, height=500, returned_objects=[])

#         # ========================================================
#         # TAB 2: AI REASONING & DISPATCH
#         # ========================================================
#         with tab2:
#             st.subheader("AI Reasoning & Dispatch Plan")

#             st.caption(
#                 "This forecast is generated using the trained Traffic Impact Prediction model "
#                 "built on historical event cause, priority, event type, road closure, and junction patterns."
#             )

#             x1, x2, x3 = st.columns(3)

#             x1.info(
#                 f"🥇 Primary Operational Driver\n\n**Event Cause:** {event_cause.replace('_', ' ').title()}"
#             )

#             x2.warning(
#                 f"🥈 Secondary Driver\n\n**Priority:** {priority}"
#             )

#             x3.error(
#                 f"🥉 Tertiary Driver\n\n**Road Closure Required:** {requires_road_closure}"
#             )

#             st.markdown("---")
#             st.subheader("Recommended Operational Actions")

#             for action in rec["actions"]:
#                 st.write(f"✅ {action}")

#             st.markdown("---")
#             st.subheader("Dispatch Summary")

#             dispatch_text = f"""
# 🚨 ASTraM TRAFFIC DISPATCH ALERT 🚨

# Predicted Event Impact Forecast
# --------------------------------
# Event Cause       : {event_cause.replace('_', ' ').title()}
# Event Type        : {event_type.title()}
# Priority          : {priority}
# Road Closure      : {requires_road_closure}
# Zone              : {selected_zone}
# Police Station    : {selected_station}
# Junction          : {selected_junction}

# Predicted Traffic Impact Index : {predicted_impact:.2f}
# Predicted Risk Level          : {predicted_risk}

# Recommended Deployment
# --------------------------------
# Traffic Officers   : {rec['officers']}
# Barricades         : {rec['barricades']}
# Diversion Required : {rec['diversion_required']}
# Diversion Plan     : {rec['diversion']}

# Suggested Actions
# --------------------------------
# 1. {rec['actions'][0]}
# 2. {rec['actions'][1]}
# 3. {rec['actions'][2]}
# 4. {rec['actions'][3]}

# Incident Notes
# --------------------------------
# {description_input if description_input.strip() else "No additional incident notes provided."}
# """
#             st.code(dispatch_text, language="markdown")

#         # ========================================================
#         # TAB 3: POST-EVENT LEARNING LOOP
#         # ========================================================
#         with tab3:
#             st.subheader("Post-Event Learning Loop")

#             st.caption(
#                 "After the incident is resolved, enter the actual field outcome. "
#                 "This creates a retraining log for future model refinement."
#             )

#             with st.form("feedback_form"):
#                 cA, cB = st.columns(2)

#                 actual_time = cA.number_input(
#                     "Actual Clearance Time (Minutes)",
#                     min_value=5,
#                     max_value=500,
#                     value=60
#                 )

#                 actual_officers = cB.number_input(
#                     "Actual Officers Used",
#                     min_value=1,
#                     max_value=20,
#                     value=rec["officers"]
#                 )

#                 actual_barricades = st.number_input(
#                     "Actual Barricades Used",
#                     min_value=0,
#                     max_value=20,
#                     value=rec["barricades"]
#                 )

#                 was_prediction_accurate = st.radio(
#                     "Was the forecast accurate?",
#                     [
#                         "Yes",
#                         "No - Predicted Too High",
#                         "No - Predicted Too Low"
#                     ],
#                     horizontal=True
#                 )

#                 submit_feedback = st.form_submit_button("💾 Save to Retraining Log")

#                 if submit_feedback:
#                     feedback_row = {
#                         "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
#                         "event_cause": event_cause,
#                         "event_type": event_type,
#                         "priority": priority,
#                         "requires_road_closure": requires_road_closure,
#                         "zone": selected_zone,
#                         "police_station": selected_station,
#                         "junction": selected_junction,
#                         "predicted_impact": predicted_impact,
#                         "predicted_risk": predicted_risk,
#                         "recommended_officers": rec["officers"],
#                         "recommended_barricades": rec["barricades"],
#                         "recommended_diversion_required": rec["diversion_required"],
#                         "recommended_diversion_plan": rec["diversion"],
#                         "actual_clearance_mins": actual_time,
#                         "actual_officers_used": actual_officers,
#                         "actual_barricades_used": actual_barricades,
#                         "prediction_feedback": was_prediction_accurate,
#                         "notes": description_input
#                     }

#                     try:
#                         saved_path = save_feedback_log(
#                             feedback_row,
#                             "astram_retraining_log.csv"
#                         )
#                         st.success("✅ Feedback logged successfully.")
#                         st.info(f"Saved to: {saved_path}")
#                     except Exception as e:
#                         st.error(f"❌ Error saving feedback: {e}")

#             st.markdown("### Saved Feedback History")
#             log_file = os.path.abspath("astram_retraining_log.csv")

#             if os.path.exists(log_file):
#                 try:
#                     log_df = pd.read_csv(log_file)
#                     st.dataframe(log_df, use_container_width=True)
#                     st.caption(f"Current log file: {log_file}")
#                 except Exception as e:
#                     st.error(f"Could not read retraining log: {e}")
#             else:
#                 st.info("No retraining log found yet. Submit one feedback record first.")

#     else:
#         st.info("👈 Fill the incident details in the sidebar and click **Analyze Incident**.")

# # ============================================================
# # PAGE 3: HOTSPOT INTELLIGENCE
# # ============================================================

# elif page == "Hotspot Intelligence":

#     st.subheader("🔥 Historical Hotspot Intelligence")

#     st.markdown(
#         """
#         This module highlights historical junction-level traffic hotspots derived from
#         event frequency and Traffic Impact Index patterns.
#         """
#     )

#     hotspot_display = hotspots[
#         ["junction", "event_count", "avg_impact", "risk_level"]
#     ].copy()

#     hotspot_display.columns = [
#         "Junction",
#         "Events",
#         "Traffic Impact Index",
#         "Risk Level"
#     ]

#     st.dataframe(hotspot_display.head(30), use_container_width=True)

#     st.markdown("---")
#     st.subheader("Interactive Hotspot Map")

#     if os.path.exists("traffic_hotspots_final.html"):
#         with open("traffic_hotspots_final.html", "r", encoding="utf-8") as f:
#             map_html = f.read()

#         components.html(
#             map_html,
#             height=750,
#             scrolling=True
#         )
#     else:
#         st.warning("⚠️ `traffic_hotspots_final.html` not found in the project folder.")

# # ============================================================
# # PAGE 4: EVENT ANALYTICS
# # ============================================================

# elif page == "Event Analytics":

#     st.subheader("📊 Event Analytics & Operational Patterns")

#     row1_col1, row1_col2 = st.columns(2)

#     with row1_col1:
#         st.markdown("### Event Cause Distribution")
#         cause_df = (
#             df["event_cause"]
#             .value_counts()
#             .reset_index()
#         )
#         cause_df.columns = ["Event Cause", "Count"]

#         fig = px.bar(
#             cause_df.head(15),
#             x="Event Cause",
#             y="Count",
#             title="Event Cause Distribution"
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     with row1_col2:
#         st.markdown("### Priority Distribution")
#         priority_df = (
#             df["priority"]
#             .value_counts()
#             .reset_index()
#         )
#         priority_df.columns = ["Priority", "Count"]

#         fig = px.pie(
#             priority_df,
#             names="Priority",
#             values="Count",
#             title="Priority Distribution"
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     st.markdown("---")

#     row2_col1, row2_col2 = st.columns(2)

#     with row2_col1:
#         st.markdown("### Planned vs Unplanned Events")
#         type_df = (
#             df["event_type"]
#             .value_counts()
#             .reset_index()
#         )
#         type_df.columns = ["Event Type", "Count"]

#         fig = px.bar(
#             type_df,
#             x="Event Type",
#             y="Count",
#             title="Planned vs Unplanned Events"
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     with row2_col2:
#         st.markdown("### Top Police Stations by Event Volume")
#         if "police_station" in df.columns:
#             ps_df = (
#                 df["police_station"]
#                 .value_counts()
#                 .reset_index()
#                 .head(10)
#             )
#             ps_df.columns = ["Police Station", "Count"]

#             fig = px.bar(
#                 ps_df,
#                 x="Police Station",
#                 y="Count",
#                 title="Top Police Stations"
#             )
#             st.plotly_chart(fig, use_container_width=True)

#     st.markdown("---")

#     st.markdown("### Junction Hotspot Summary")
#     hotspot_summary = hotspots[
#         ["junction", "event_count", "avg_impact", "risk_level"]
#     ].head(20).copy()

#     hotspot_summary.columns = [
#         "Junction",
#         "Events",
#         "Traffic Impact Index",
#         "Risk Level"
#     ]

#     st.dataframe(hotspot_summary, use_container_width=True)


import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ASTraM Command Center",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("ASTraM Command Center")
st.markdown(
    """
    **AI-Driven Event Impact Forecasting & Resource Deployment for Bengaluru Traffic Police**
    """
)

# ============================================================
# FILE PATHS
# ============================================================

DATA_FILE = "impact_dataset.csv"
MODEL_FILE = "traffic_impact_predictor.pkl"
RETRAIN_LOG_FILE = "astram_retraining_log.csv"

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    # Safe numeric conversion
    for col in ["latitude", "longitude", "impact_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill common nulls used in app
    for col in ["event_cause", "priority", "event_type", "police_station", "zone", "junction"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    # Standardize casing
    if "priority" in df.columns:
        df["priority"] = df["priority"].astype(str).str.strip().replace({
            "high": "High",
            "low": "Low"
        })

    if "event_type" in df.columns:
        df["event_type"] = df["event_type"].astype(str).str.strip().str.lower()

    return df


@st.cache_resource
def load_model():
    if os.path.exists(MODEL_FILE):
        model = joblib.load(MODEL_FILE)
        return model, True
    return None, False


def ensure_retraining_log_schema(log_file=RETRAIN_LOG_FILE):
    """
    Ensure the retraining log exists with the required columns.
    Also fixes empty/corrupt file situations.
    """
    required_columns = [
        "timestamp",
        "event_cause",
        "event_type",
        "priority",
        "requires_road_closure",
        "zone",
        "police_station",
        "junction",
        "predicted_impact",
        "predicted_risk",
        "recommended_officers",
        "recommended_barricades",
        "recommended_diversion_required",
        "recommended_diversion_plan",
        "actual_clearance_mins",
        "actual_officers_used",
        "actual_barricades_used",
        "actual_diversion_required",
        "prediction_feedback",
        "observed_field_impact_score",
        "impact_error",
        "notes"
    ]

    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        pd.DataFrame(columns=required_columns).to_csv(log_file, index=False)
        return

    try:
        existing = pd.read_csv(log_file)
    except Exception:
        pd.DataFrame(columns=required_columns).to_csv(log_file, index=False)
        return

    for col in required_columns:
        if col not in existing.columns:
            existing[col] = np.nan

    existing = existing[required_columns]
    existing.to_csv(log_file, index=False)


def load_retraining_log(log_file=RETRAIN_LOG_FILE):
    """
    Safe retraining log loader.
    """
    ensure_retraining_log_schema(log_file)

    try:
        log_df = pd.read_csv(log_file)
    except Exception:
        return pd.DataFrame()

    if log_df.empty:
        return log_df

    # Standardize text columns
    text_cols = [
        "event_cause", "event_type", "priority", "zone",
        "police_station", "junction",
        "recommended_diversion_required",
        "actual_diversion_required",
        "prediction_feedback"
    ]
    for col in text_cols:
        if col in log_df.columns:
            log_df[col] = log_df[col].fillna("Unknown").astype(str).str.strip()

    # Standardize booleans
    if "requires_road_closure" in log_df.columns:
        log_df["requires_road_closure"] = log_df["requires_road_closure"].astype(str).str.lower().map({
            "true": True,
            "false": False
        }).fillna(log_df["requires_road_closure"])

    # Numeric conversions
    numeric_cols = [
        "predicted_impact",
        "recommended_officers",
        "recommended_barricades",
        "actual_clearance_mins",
        "actual_officers_used",
        "actual_barricades_used",
        "observed_field_impact_score",
        "impact_error"
    ]
    for col in numeric_cols:
        if col in log_df.columns:
            log_df[col] = pd.to_numeric(log_df[col], errors="coerce")

    return log_df


df = load_data()
model, model_loaded = load_model()
ensure_retraining_log_schema(RETRAIN_LOG_FILE)

if not model_loaded:
    st.error("⚠️ Model file `traffic_impact_predictor.pkl` not found in the project folder.")
    st.stop()

# ============================================================
# SESSION STATE INIT
# ============================================================

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "analysis_payload" not in st.session_state:
    st.session_state.analysis_payload = {}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_risk(impact):
    if impact >= 75:
        return "HIGH"
    elif impact >= 55:
        return "MEDIUM"
    return "LOW"


def get_pin_color(risk):
    if risk == "HIGH":
        return "red"
    elif risk == "MEDIUM":
        return "orange"
    return "green"


def get_operational_radius(risk):
    if risk == "HIGH":
        return 2500
    elif risk == "MEDIUM":
        return 1500
    return 700


def get_event_cause_score(event_cause):
    severity_map = {
        "accident": 90,
        "public_event": 85,
        "procession": 82,
        "protest": 85,
        "construction": 75,
        "water_logging": 78,
        "vehicle_breakdown": 60,
        "congestion": 70,
        "tree_fall": 72,
        "pot_holes": 45,
        "road_conditions": 50,
        "others": 55,
        "debris": 58,
        "fog_low_visibility": 62,
        "vip_movement": 88,
        "test_demo": 65
    }
    return severity_map.get(str(event_cause).strip(), 55)


def get_priority_score(priority):
    return 100 if str(priority).strip().lower() == "high" else 40


def get_closure_score(requires_road_closure):
    return 100 if bool(requires_road_closure) else 20


def get_event_type_score(event_type):
    return 65 if str(event_type).strip().lower() == "planned" else 50


def get_hotspot_score(hotspot_event_count=None, hotspot_avg_impact=None):
    if hotspot_event_count is None and hotspot_avg_impact is None:
        return 40

    event_component = 0
    impact_component = 0

    if hotspot_event_count is not None:
        event_component = min((hotspot_event_count / 60) * 100, 100)

    if hotspot_avg_impact is not None:
        impact_component = min(hotspot_avg_impact, 100)

    if hotspot_event_count is not None and hotspot_avg_impact is not None:
        return round((event_component * 0.45) + (impact_component * 0.55), 2)
    elif hotspot_avg_impact is not None:
        return round(impact_component, 2)
    else:
        return round(event_component, 2)


def get_diversion_plan(impact, requires_road_closure, event_cause, rns):
    high_diversion_causes = {
        "public_event", "procession", "protest",
        "construction", "water_logging", "vip_movement"
    }

    if requires_road_closure or rns >= 85:
        return {
            "diversion_required": "YES",
            "diversion_level": "CORRIDOR",
            "diversion_plan": "Activate corridor-level diversion and upstream traffic advisory 1-2 km before the incident."
        }

    if event_cause in high_diversion_causes and impact >= 65:
        return {
            "diversion_required": "YES",
            "diversion_level": "JUNCTION",
            "diversion_plan": "Implement junction-level diversion and pre-position barricades on feeder roads."
        }

    if event_cause in {"public_event", "procession", "protest", "construction", "vip_movement"} and impact >= 55:
        return {
            "diversion_required": "MAYBE",
            "diversion_level": "LOCAL",
            "diversion_plan": "Prepare a preventive diversion advisory and stage barricades at nearby feeder routes."
        }

    if impact >= 55 or rns >= 65:
        return {
            "diversion_required": "MAYBE",
            "diversion_level": "LOCAL",
            "diversion_plan": "Keep local alternate route advisory ready and divert traffic if queue builds."
        }

    return {
        "diversion_required": "NO",
        "diversion_level": "NONE",
        "diversion_plan": "No diversion required. Maintain routine monitoring."
    }


def compute_resource_need_score(
    impact,
    event_cause,
    priority,
    requires_road_closure,
    event_type,
    hotspot_event_count=None,
    hotspot_avg_impact=None
):
    priority_score = get_priority_score(priority)
    closure_score = get_closure_score(requires_road_closure)
    cause_score = get_event_cause_score(event_cause)
    event_type_score = get_event_type_score(event_type)
    hotspot_score = get_hotspot_score(hotspot_event_count, hotspot_avg_impact)

    rns = (
        impact * 0.40 +
        priority_score * 0.15 +
        closure_score * 0.15 +
        cause_score * 0.15 +
        event_type_score * 0.05 +
        hotspot_score * 0.10
    )

    return round(rns, 2)


def recommend_resources(
    impact,
    requires_road_closure=False,
    event_cause="others",
    priority="Low",
    event_type="unplanned",
    hotspot_event_count=None,
    hotspot_avg_impact=None
):
    rns = compute_resource_need_score(
        impact=impact,
        event_cause=event_cause,
        priority=priority,
        requires_road_closure=requires_road_closure,
        event_type=event_type,
        hotspot_event_count=hotspot_event_count,
        hotspot_avg_impact=hotspot_avg_impact
    )

    if rns < 45:
        risk = "LOW"
        officers = 2
        barricades = 1
        resource_category = "LOW"
    elif rns < 60:
        risk = "LOW"
        officers = 3
        barricades = 2
        resource_category = "LOW"
    elif rns < 75:
        risk = "MEDIUM"
        officers = 4
        barricades = 4
        resource_category = "MEDIUM"
    elif rns < 90:
        risk = "HIGH"
        officers = 5
        barricades = 5
        resource_category = "HIGH"
    else:
        risk = "HIGH"
        officers = 6
        barricades = 7
        resource_category = "HIGH"

    officer_adj = 0
    barricade_adj = 0

    if event_cause == "accident":
        officer_adj += 1
        barricade_adj += 1
    elif event_cause in ["public_event", "procession", "protest", "vip_movement"]:
        officer_adj += 1
        barricade_adj += 2
    elif event_cause in ["construction", "water_logging", "tree_fall"]:
        barricade_adj += 2
    elif event_cause == "vehicle_breakdown":
        officer_adj += 1
        if impact >= 70:
            barricade_adj += 1
    elif event_cause == "congestion":
        officer_adj += 1

    if str(priority).strip().lower() == "high":
        officer_adj += 1

    if requires_road_closure:
        officer_adj += 1
        barricade_adj += 1

    if str(event_type).strip().lower() == "planned":
        barricade_adj += 1
        if event_cause in ["public_event", "procession", "protest", "construction", "vip_movement"]:
            barricade_adj += 1
    else:
        if event_cause in ["accident", "vehicle_breakdown", "tree_fall", "water_logging", "congestion"]:
            officer_adj += 1

    hotspot_score = get_hotspot_score(hotspot_event_count, hotspot_avg_impact)
    if hotspot_score >= 75:
        barricade_adj += 1
    elif hotspot_score >= 60 and risk != "LOW":
        barricade_adj += 1

    officer_adj = min(officer_adj, 3)
    barricade_adj = min(barricade_adj, 4)

    officers += officer_adj
    barricades += barricade_adj

    if risk == "LOW":
        officers = min(officers, 4)
        barricades = min(barricades, 4)
    elif risk == "MEDIUM":
        officers = min(officers, 6)
        barricades = min(barricades, 6)
    else:
        officers = min(officers, 8)
        barricades = min(barricades, 9)

    diversion_info = get_diversion_plan(
        impact=impact,
        requires_road_closure=requires_road_closure,
        event_cause=event_cause,
        rns=rns
    )

    actions = []

    if risk == "HIGH":
        actions.append("Deploy Traffic Response Team immediately")
    elif risk == "MEDIUM":
        actions.append("Deploy additional traffic personnel")
    else:
        actions.append("Routine monitoring")

    if barricades >= 5:
        actions.append("Install temporary barricades at approach roads")
    else:
        actions.append("Place temporary barricades near congestion points")

    if diversion_info["diversion_required"] == "YES":
        actions.append("Activate diversion route and public traffic advisory")
    elif diversion_info["diversion_required"] == "MAYBE":
        actions.append("Keep alternate route advisory ready; divert if queue builds")
    else:
        actions.append("No diversion required")

    if risk == "HIGH":
        actions.append("Continuous live monitoring until clearance")
    elif risk == "MEDIUM":
        actions.append("Coordinate with nearest police station")
    else:
        actions.append("Keep response team on low alert")

    return {
        "risk": risk,
        "officers": int(officers),
        "barricades": int(barricades),
        "resource_category": resource_category,
        "diversion_required": diversion_info["diversion_required"],
        "diversion": diversion_info["diversion_plan"],
        "actions": actions[:4]
    }


def build_hotspot_table(data):
    hotspot_df = (
        data[data["junction"].notna()]
        .groupby("junction")
        .agg(
            event_count=("junction", "count"),
            avg_impact=("impact_score", "mean"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean")
        )
        .reset_index()
        .sort_values(by=["event_count", "avg_impact"], ascending=False)
    )

    hotspot_df["risk_level"] = hotspot_df["avg_impact"].apply(get_risk)
    return hotspot_df


def get_filtered_junctions(data, selected_zone="Unknown", selected_station="Unknown"):
    temp = data.copy()

    if selected_zone != "Unknown" and "zone" in temp.columns:
        temp = temp[temp["zone"] == selected_zone]

    if selected_station != "Unknown" and "police_station" in temp.columns:
        temp = temp[temp["police_station"] == selected_station]

    junctions = sorted(
        temp["junction"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    if len(junctions) == 0:
        return ["Unknown"]

    return junctions


# ============================================================
# POST-EVENT IMPACT CALCULATION
# ============================================================

def calculate_observed_field_impact_score(
    actual_clearance_mins,
    actual_officers_used,
    actual_barricades_used,
    prediction_feedback
):
    """
    Converts actual field outcome into an observed impact score (0-100).
    This does NOT retrain the original model logic directly;
    it creates field-truth learning signal for adaptive refinement.
    """

    # Clearance time contribution (dominant)
    # 30 mins -> low, 180+ -> very high
    clearance_score = min((actual_clearance_mins / 180) * 100, 100)

    # Officers contribution
    officers_score = min((actual_officers_used / 10) * 100, 100)

    # Barricade contribution
    barricade_score = min((actual_barricades_used / 10) * 100, 100)

    # Feedback correction
    feedback_adjustment = 0
    if prediction_feedback == "No - Predicted Too High":
        feedback_adjustment = -8
    elif prediction_feedback == "No - Predicted Too Low":
        feedback_adjustment = 8

    observed = (
        clearance_score * 0.60 +
        officers_score * 0.25 +
        barricade_score * 0.15
    ) + feedback_adjustment

    observed = max(0, min(observed, 100))
    return round(observed, 2)


def save_feedback_log(feedback_dict, log_file=RETRAIN_LOG_FILE):
    """
    Safe feedback logger with schema protection.
    """
    ensure_retraining_log_schema(log_file)

    feedback_df = pd.DataFrame([feedback_dict])

    try:
        existing = pd.read_csv(log_file)
    except Exception:
        existing = pd.DataFrame(columns=feedback_df.columns)

    # Add any missing columns to existing
    for col in feedback_df.columns:
        if col not in existing.columns:
            existing[col] = np.nan

    # Add any missing columns to feedback row
    for col in existing.columns:
        if col not in feedback_df.columns:
            feedback_df[col] = np.nan

    # Align order
    feedback_df = feedback_df[existing.columns]

    updated_df = pd.concat([existing, feedback_df], ignore_index=True)
    updated_df.to_csv(log_file, index=False)

    return os.path.abspath(log_file)

# ============================================================
# ADAPTIVE LEARNING ENGINE
# ============================================================

def normalize_diversion_value(x):
    """
    Normalize diversion labels from feedback.
    """
    x = str(x).strip().upper()
    if x in ["YES", "Y", "TRUE"]:
        return "YES"
    if x in ["NO", "N", "FALSE"]:
        return "NO"
    if x in ["MAYBE", "PARTIAL", "OPTIONAL"]:
        return "MAYBE"
    return "NO"


def majority_vote_diversion(series):
    """
    Majority voting for diversion decision.
    Priority rule on tie:
    YES > MAYBE > NO
    """
    if series is None or len(series) == 0:
        return None

    s = pd.Series(series).dropna().astype(str).apply(normalize_diversion_value)
    if s.empty:
        return None

    counts = s.value_counts()

    yes_count = counts.get("YES", 0)
    maybe_count = counts.get("MAYBE", 0)
    no_count = counts.get("NO", 0)

    max_count = max(yes_count, maybe_count, no_count)

    tied = []
    if yes_count == max_count:
        tied.append("YES")
    if maybe_count == max_count:
        tied.append("MAYBE")
    if no_count == max_count:
        tied.append("NO")

    # Tie priority
    if "YES" in tied:
        return "YES"
    elif "MAYBE" in tied:
        return "MAYBE"
    return "NO"


def build_diversion_plan_from_vote(vote):
    vote = normalize_diversion_value(vote)

    if vote == "YES":
        return "Activate diversion route and upstream advisory based on similar past field outcomes."
    elif vote == "MAYBE":
        return "Keep diversion route prepared and activate if queue builds, based on similar past field outcomes."
    return "No diversion usually required for similar past scenarios; maintain monitoring."


def get_similar_feedback_logs(
    log_df,
    event_cause,
    event_type,
    priority,
    requires_road_closure,
    junction
):
    """
    3-step adaptive learning retrieval:

    STEP 1: Exact scenario
    STEP 2: Semi-similar scenario
    STEP 3: Broad similar scenario
    """

    if log_df is None or log_df.empty:
        return {
            "step1_exact": pd.DataFrame(),
            "step2_similar": pd.DataFrame(),
            "step3_broad": pd.DataFrame()
        }

    work = log_df.copy()

    # STEP 1: exact scenario
    step1 = work[
        (work["event_cause"] == event_cause) &
        (work["event_type"] == event_type) &
        (work["priority"] == priority) &
        (work["requires_road_closure"] == requires_road_closure) &
        (work["junction"] == junction)
    ].copy()

    # STEP 2: same cause + priority + junction
    step2 = work[
        (work["event_cause"] == event_cause) &
        (work["priority"] == priority) &
        (work["junction"] == junction)
    ].copy()

    # STEP 3: same cause only OR same junction only
    step3 = work[
        (work["event_cause"] == event_cause) |
        (work["junction"] == junction)
    ].copy()

    return {
        "step1_exact": step1,
        "step2_similar": step2,
        "step3_broad": step3
    }


def apply_adaptive_learning(
    base_rec,
    predicted_impact,
    event_cause,
    event_type,
    priority,
    requires_road_closure,
    junction,
    retrain_log_df
):
    """
    Hybrid 3-step adaptive learning.

    Output:
    - adjusted officers
    - adjusted barricades
    - diversion_required learned from majority voting
    - explanation metadata
    """

    # No logs => base recommendation
    if retrain_log_df is None or retrain_log_df.empty:
        result = base_rec.copy()
        result["adaptive_learning_used"] = False
        result["learning_summary"] = "No historical feedback logs available yet."
        return result

    matches = get_similar_feedback_logs(
        retrain_log_df,
        event_cause=event_cause,
        event_type=event_type,
        priority=priority,
        requires_road_closure=requires_road_closure,
        junction=junction
    )

    step1 = matches["step1_exact"]
    step2 = matches["step2_similar"]
    step3 = matches["step3_broad"]

    result = base_rec.copy()

    # ------------------------------------------------------------
    # STEP 1: EXACT SCENARIO LEARNING
    # ------------------------------------------------------------
    if len(step1) >= 1:
        # weighted blend for 1-log case, average for multiple
        avg_off = step1["actual_officers_used"].dropna().mean()
        avg_bar = step1["actual_barricades_used"].dropna().mean()
        diversion_vote = majority_vote_diversion(step1["actual_diversion_required"])

        if len(step1) == 1:
            # 1-log hybrid blend
            result["officers"] = int(round((base_rec["officers"] * 0.60) + (avg_off * 0.40)))
            result["barricades"] = int(round((base_rec["barricades"] * 0.60) + (avg_bar * 0.40)))
        else:
            # 2+ logs stronger learning
            result["officers"] = int(round((base_rec["officers"] * 0.35) + (avg_off * 0.65)))
            result["barricades"] = int(round((base_rec["barricades"] * 0.35) + (avg_bar * 0.65)))

        if diversion_vote is not None:
            result["diversion_required"] = diversion_vote
            result["diversion"] = build_diversion_plan_from_vote(diversion_vote)

        result["adaptive_learning_used"] = True
        result["learning_summary"] = (
            f"Adaptive learning applied from EXACT scenario history "
            f"({len(step1)} matching feedback log(s))."
        )
        return result

    # ------------------------------------------------------------
    # STEP 2: SIMILAR SCENARIO LEARNING
    # ------------------------------------------------------------
    if len(step2) >= 2:
        avg_off = step2["actual_officers_used"].dropna().mean()
        avg_bar = step2["actual_barricades_used"].dropna().mean()
        diversion_vote = majority_vote_diversion(step2["actual_diversion_required"])

        result["officers"] = int(round((base_rec["officers"] * 0.50) + (avg_off * 0.50)))
        result["barricades"] = int(round((base_rec["barricades"] * 0.50) + (avg_bar * 0.50)))

        if diversion_vote is not None:
            result["diversion_required"] = diversion_vote
            result["diversion"] = build_diversion_plan_from_vote(diversion_vote)

        result["adaptive_learning_used"] = True
        result["learning_summary"] = (
            f"Adaptive learning applied from SIMILAR scenario history "
            f"({len(step2)} similar feedback log(s))."
        )
        return result

    # ------------------------------------------------------------
    # STEP 3: BROAD SIMILAR FALLBACK
    # ------------------------------------------------------------
    if len(step3) >= 3:
        avg_off = step3["actual_officers_used"].dropna().mean()
        avg_bar = step3["actual_barricades_used"].dropna().mean()
        diversion_vote = majority_vote_diversion(step3["actual_diversion_required"])

        result["officers"] = int(round((base_rec["officers"] * 0.70) + (avg_off * 0.30)))
        result["barricades"] = int(round((base_rec["barricades"] * 0.70) + (avg_bar * 0.30)))

        if diversion_vote is not None:
            result["diversion_required"] = diversion_vote
            result["diversion"] = build_diversion_plan_from_vote(diversion_vote)

        result["adaptive_learning_used"] = True
        result["learning_summary"] = (
            f"Adaptive learning applied from BROAD similar history "
            f"({len(step3)} broader feedback log(s))."
        )
        return result

    # No sufficient learning signal
    result["adaptive_learning_used"] = False
    result["learning_summary"] = "No sufficient similar feedback history yet. Using model-based recommendation."
    return result


hotspots = build_hotspot_table(df)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard Overview",
        "Forecasting Command Center",
        "Hotspot Intelligence",
        "Event Analytics"
    ]
)

# ============================================================
# PAGE 1: DASHBOARD OVERVIEW
# ============================================================

if page == "Dashboard Overview":

    st.subheader("Citywide Traffic Event Overview")

    total_events = len(df)
    planned_events = (df["event_type"] == "planned").sum()
    unplanned_events = (df["event_type"] == "unplanned").sum()
    high_priority_events = (df["priority"].str.lower() == "high").sum()
    avg_impact = df["impact_score"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Events", total_events)
    c2.metric("Planned Events", planned_events)
    c3.metric("Unplanned Events", unplanned_events)
    c4.metric("High Priority Events", high_priority_events)
    c5.metric("Avg Traffic Impact Index", f"{avg_impact:.2f}")

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("Top Event Causes")
        cause_counts = df["event_cause"].value_counts().reset_index()
        cause_counts.columns = ["Event Cause", "Count"]

        fig1 = px.bar(
            cause_counts.head(10),
            x="Event Cause",
            y="Count",
            title="Top Event Causes"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        st.subheader("Priority Distribution")
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]

        fig2 = px.pie(
            priority_counts,
            names="Priority",
            values="Count",
            title="Priority Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    st.subheader("Top Junction Hotspots")

    hotspot_preview = hotspots[
        ["junction", "event_count", "avg_impact", "risk_level"]
    ].head(10).copy()

    hotspot_preview.columns = [
        "Junction",
        "Events",
        "Traffic Impact Index",
        "Risk Level"
    ]

    st.dataframe(hotspot_preview, use_container_width=True)

    st.info(
        """
        **What this system does**
        - Forecasts event-related traffic impact from historical incident patterns
        - Identifies recurring congestion hotspots
        - Recommends officers, barricades, and whether diversion is required
        - Learns from actual field outcomes using a post-event learning loop
        """
    )

# ============================================================
# PAGE 2: FORECASTING COMMAND CENTER
# ============================================================

elif page == "Forecasting Command Center":

    st.subheader("🚨 Incident Forecasting & Resource Deployment")

    st.sidebar.header("Incident Input")

    event_cause_options = sorted(df["event_cause"].dropna().unique().tolist())
    event_type_options = sorted(df["event_type"].dropna().unique().tolist())
    priority_options = ["High", "Low"]

    event_cause = st.sidebar.selectbox("Event Cause", event_cause_options)
    event_type = st.sidebar.selectbox("Event Type", event_type_options)
    priority = st.sidebar.selectbox("Priority", priority_options)

    requires_road_closure = st.sidebar.radio(
        "Requires Road Closure?",
        [True, False],
        horizontal=True
    )

    st.sidebar.divider()
    st.sidebar.subheader("📍 Operational Context")

    zone_options = ["Unknown"] + sorted(
        [z for z in df["zone"].dropna().unique().tolist() if z != "Unknown"]
    ) if "zone" in df.columns else ["Unknown"]

    police_options = ["Unknown"] + sorted(
        [p for p in df["police_station"].dropna().unique().tolist() if p != "Unknown"]
    ) if "police_station" in df.columns else ["Unknown"]

    selected_zone = st.sidebar.selectbox("Zone", zone_options)
    selected_station = st.sidebar.selectbox("Police Station", police_options)

    junction_options = get_filtered_junctions(df, selected_zone, selected_station)
    selected_junction = st.sidebar.selectbox("Junction", junction_options)

    description_input = st.sidebar.text_area(
        "Incident Notes (optional)",
        placeholder="e.g. heavy vehicle breakdown near junction causing lane blockage"
    )

    st.sidebar.divider()
    show_hotspots = st.sidebar.checkbox("Overlay Historical Hotspots", value=True)

    analyze_btn = st.sidebar.button("🚨 Analyze Incident", use_container_width=True)

    if analyze_btn:
        # ========================================================
        # MODEL INPUT
        # ========================================================
        input_df = pd.DataFrame({
            "event_cause": [event_cause],
            "priority": [priority],
            "requires_road_closure": [requires_road_closure],
            "event_type": [event_type],
            "junction": [selected_junction]
        })

        predicted_impact = float(model.predict(input_df)[0])
        predicted_risk = get_risk(predicted_impact)

        # ========================================================
        # FILTER HISTORICAL DATA AROUND THE SELECTED CONTEXT
        # ========================================================
        filtered_df = df.copy()

        if selected_junction != "Unknown" and "junction" in filtered_df.columns:
            temp = filtered_df[filtered_df["junction"] == selected_junction]
            if len(temp) > 0:
                filtered_df = temp
            else:
                filtered_df = df[df["event_cause"] == event_cause].copy()
        else:
            filtered_df = df[df["event_cause"] == event_cause].copy()

        if selected_zone != "Unknown" and "zone" in filtered_df.columns:
            temp = filtered_df[filtered_df["zone"] == selected_zone]
            if len(temp) > 0:
                filtered_df = temp

        if selected_station != "Unknown" and "police_station" in filtered_df.columns:
            temp = filtered_df[filtered_df["police_station"] == selected_station]
            if len(temp) > 0:
                filtered_df = temp

        # ========================================================
        # MAP LOCATION SELECTION
        # ========================================================
        if len(filtered_df) > 0 and filtered_df["latitude"].notna().sum() > 0:
            selected_lat = filtered_df["latitude"].dropna().mean()
            selected_lon = filtered_df["longitude"].dropna().mean()
        else:
            selected_lat = df["latitude"].dropna().mean()
            selected_lon = df["longitude"].dropna().mean()

        selected_coords = [selected_lat, selected_lon]

        # ========================================================
        # RELATED HOTSPOT
        # ========================================================
        related_hotspot = None

        if selected_junction != "Unknown":
            temp_hotspot = hotspots[hotspots["junction"] == selected_junction]
            if len(temp_hotspot) > 0:
                related_hotspot = temp_hotspot.head(1)

        if related_hotspot is None and "junction" in filtered_df.columns and filtered_df["junction"].notna().sum() > 0:
            related_hotspot = (
                filtered_df[filtered_df["junction"].notna()]
                .groupby("junction")
                .agg(
                    event_count=("junction", "count"),
                    avg_impact=("impact_score", "mean")
                )
                .reset_index()
                .sort_values(by=["event_count", "avg_impact"], ascending=False)
                .head(1)
            )

        hotspot_event_count = None
        hotspot_avg_impact = None

        if related_hotspot is not None and len(related_hotspot) > 0:
            hotspot_event_count = int(related_hotspot.iloc[0]["event_count"])
            hotspot_avg_impact = float(related_hotspot.iloc[0]["avg_impact"])

        # ========================================================
        # BASE RESOURCE RECOMMENDATION
        # ========================================================
        base_rec = recommend_resources(
            impact=predicted_impact,
            requires_road_closure=requires_road_closure,
            event_cause=event_cause,
            priority=priority,
            event_type=event_type,
            hotspot_event_count=hotspot_event_count,
            hotspot_avg_impact=hotspot_avg_impact
        )

        # ========================================================
        # ADAPTIVE LEARNING OVERLAY
        # ========================================================
        retrain_log_df = load_retraining_log(RETRAIN_LOG_FILE)

        rec = apply_adaptive_learning(
            base_rec=base_rec,
            predicted_impact=predicted_impact,
            event_cause=event_cause,
            event_type=event_type,
            priority=priority,
            requires_road_closure=requires_road_closure,
            junction=selected_junction,
            retrain_log_df=retrain_log_df
        )

        # ========================================================
        # STORE ANALYSIS IN SESSION STATE
        # ========================================================
        st.session_state.analysis_done = True
        st.session_state.analysis_payload = {
            "event_cause": event_cause,
            "event_type": event_type,
            "priority": priority,
            "requires_road_closure": requires_road_closure,
            "selected_zone": selected_zone,
            "selected_station": selected_station,
            "selected_junction": selected_junction,
            "description_input": description_input,
            "predicted_impact": predicted_impact,
            "predicted_risk": predicted_risk,
            "selected_coords": selected_coords,
            "related_hotspot": related_hotspot,
            "rec": rec,
            "show_hotspots": show_hotspots,
            "learning_used": rec.get("adaptive_learning_used", False),
            "learning_summary": rec.get("learning_summary", "")
        }

    # ========================================================
    # RENDER FROM SESSION STATE
    # ========================================================
    if st.session_state.analysis_done:
        payload = st.session_state.analysis_payload

        event_cause = payload["event_cause"]
        event_type = payload["event_type"]
        priority = payload["priority"]
        requires_road_closure = payload["requires_road_closure"]
        selected_zone = payload["selected_zone"]
        selected_station = payload["selected_station"]
        selected_junction = payload["selected_junction"]
        description_input = payload["description_input"]
        predicted_impact = payload["predicted_impact"]
        predicted_risk = payload["predicted_risk"]
        selected_coords = payload["selected_coords"]
        related_hotspot = payload["related_hotspot"]
        rec = payload["rec"]
        show_hotspots = payload["show_hotspots"]
        learning_used = payload["learning_used"]
        learning_summary = payload["learning_summary"]

        # ========================================================
        # MAIN ALERT BANNER
        # ========================================================
        if predicted_risk == "HIGH":
            st.error(f"🚨 HIGH IMPACT ALERT: Predicted Traffic Impact Index = {predicted_impact:.2f}")
        elif predicted_risk == "MEDIUM":
            st.warning(f"⚠️ MEDIUM IMPACT ALERT: Predicted Traffic Impact Index = {predicted_impact:.2f}")
        else:
            st.success(f"✅ LOW IMPACT ALERT: Predicted Traffic Impact Index = {predicted_impact:.2f}")

        # ========================================================
        # KPI CARDS
        # ========================================================
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Traffic Impact Index", f"{predicted_impact:.2f}")
        col2.metric("Risk Level", predicted_risk)
        col3.metric("Recommended Officers", rec["officers"])
        col4.metric("Barricades", rec["barricades"])
        col5.metric("Diversion Required", rec["diversion_required"])

        tab1, tab2, tab3 = st.tabs(
            ["Tactical Map", "AI Reasoning & Dispatch", "Post-Event Learning Loop"]
        )

        # ========================================================
        # TAB 1: TACTICAL MAP
        # ========================================================
        with tab1:
            st.subheader("Tactical Map")

            m = folium.Map(
                location=selected_coords,
                zoom_start=12,
                tiles="CartoDB dark_matter"
            )

            if show_hotspots:
                heat_df = df.dropna(subset=["latitude", "longitude", "impact_score"]).copy()
                heat_data = heat_df[["latitude", "longitude", "impact_score"]].values.tolist()

                HeatMap(
                    heat_data,
                    radius=15,
                    blur=12,
                    max_zoom=13
                ).add_to(m)

            popup_text = f"""
            <b>Forecasted Incident</b><br>
            Event Cause: {event_cause}<br>
            Event Type: {event_type}<br>
            Priority: {priority}<br>
            Junction: {selected_junction}<br>
            Requires Closure: {requires_road_closure}<br>
            Predicted TII: {predicted_impact:.2f}<br>
            Risk Level: {predicted_risk}<br>
            Officers: {rec['officers']}<br>
            Barricades: {rec['barricades']}<br>
            Diversion Required: {rec['diversion_required']}<br>
            Diversion Plan: {rec['diversion']}
            """

            folium.Marker(
                location=selected_coords,
                popup=popup_text,
                tooltip="Forecasted Incident",
                icon=folium.Icon(color=get_pin_color(predicted_risk), icon="info-sign")
            ).add_to(m)

            radius = get_operational_radius(predicted_risk)

            folium.Circle(
                location=selected_coords,
                radius=radius,
                color=get_pin_color(predicted_risk),
                fill=True,
                fill_opacity=0.35
            ).add_to(m)

            if related_hotspot is not None and len(related_hotspot) > 0:
                hotspot_name = related_hotspot.iloc[0]["junction"]
                hotspot_events = related_hotspot.iloc[0]["event_count"]
                hotspot_impact = related_hotspot.iloc[0]["avg_impact"]

                st.info(
                    f"**Closest historical pattern:** {hotspot_name} "
                    f"(Events: {hotspot_events}, Avg TII: {hotspot_impact:.2f})"
                )

            st_folium(m, width=1200, height=500, returned_objects=[])

        # ========================================================
        # TAB 2: AI REASONING & DISPATCH
        # ========================================================
        with tab2:
            st.subheader("AI Reasoning & Dispatch Plan")

            st.caption(
                "This forecast is generated using the trained Traffic Impact Prediction model "
                "built on historical event cause, priority, event type, road closure, and junction patterns."
            )

            x1, x2, x3 = st.columns(3)

            x1.info(
                f"🥇 Primary Operational Driver\n\n**Event Cause:** {event_cause.replace('_', ' ').title()}"
            )

            x2.warning(
                f"🥈 Secondary Driver\n\n**Priority:** {priority}"
            )

            x3.error(
                f"🥉 Tertiary Driver\n\n**Road Closure Required:** {requires_road_closure}"
            )

            st.markdown("---")
            st.subheader("Recommended Operational Actions")

            for action in rec["actions"]:
                st.write(f"✅ {action}")

            st.markdown("---")
            st.subheader("Dispatch Summary")

            dispatch_text = f"""
🚨 ASTraM TRAFFIC DISPATCH ALERT 🚨

Predicted Event Impact Forecast
--------------------------------
Event Cause       : {event_cause.replace('_', ' ').title()}
Event Type        : {event_type.title()}
Priority          : {priority}
Road Closure      : {requires_road_closure}
Zone              : {selected_zone}
Police Station    : {selected_station}
Junction          : {selected_junction}

Predicted Traffic Impact Index : {predicted_impact:.2f}
Predicted Risk Level          : {predicted_risk}

Recommended Deployment
--------------------------------
Traffic Officers   : {rec['officers']}
Barricades         : {rec['barricades']}
Diversion Required : {rec['diversion_required']}
Diversion Plan     : {rec['diversion']}

Adaptive Learning Status
--------------------------------
{learning_summary}

Suggested Actions
--------------------------------
1. {rec['actions'][0]}
2. {rec['actions'][1]}
3. {rec['actions'][2]}
4. {rec['actions'][3]}

Incident Notes
--------------------------------
{description_input if description_input.strip() else "No additional incident notes provided."}
"""
            st.code(dispatch_text, language="markdown")

        # ========================================================
        # TAB 3: POST-EVENT LEARNING LOOP
        # ========================================================
        with tab3:
            st.subheader("Post-Event Learning Loop")

            st.caption(
                "After the incident is resolved, enter the actual field outcome. "
                "This stores real-world outcomes for future adaptive learning."
            )

            with st.form("feedback_form"):
                cA, cB = st.columns(2)

                actual_time = cA.number_input(
                    "Actual Clearance Time (Minutes)",
                    min_value=5,
                    max_value=500,
                    value=60
                )

                actual_officers = cB.number_input(
                    "Actual Officers Used",
                    min_value=1,
                    max_value=20,
                    value=int(rec["officers"])
                )

                cC, cD = st.columns(2)

                actual_barricades = cC.number_input(
                    "Actual Barricades Used",
                    min_value=0,
                    max_value=20,
                    value=int(rec["barricades"])
                )

                actual_diversion_required = cD.selectbox(
                    "Was diversion actually required on field?",
                    ["YES", "MAYBE", "NO"],
                    index=["YES", "MAYBE", "NO"].index(rec["diversion_required"]) if rec["diversion_required"] in ["YES", "MAYBE", "NO"] else 2
                )

                was_prediction_accurate = st.radio(
                    "Was the forecast accurate?",
                    [
                        "Yes",
                        "No - Predicted Too High",
                        "No - Predicted Too Low"
                    ],
                    horizontal=True
                )

                submit_feedback = st.form_submit_button("💾 Save to Retraining Log")

                if submit_feedback:
                    observed_field_impact = calculate_observed_field_impact_score(
                        actual_clearance_mins=actual_time,
                        actual_officers_used=actual_officers,
                        actual_barricades_used=actual_barricades,
                        prediction_feedback=was_prediction_accurate
                    )

                    impact_error = round(observed_field_impact - predicted_impact, 2)

                    feedback_row = {
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "event_cause": event_cause,
                        "event_type": event_type,
                        "priority": priority,
                        "requires_road_closure": requires_road_closure,
                        "zone": selected_zone,
                        "police_station": selected_station,
                        "junction": selected_junction,
                        "predicted_impact": predicted_impact,
                        "predicted_risk": predicted_risk,
                        "recommended_officers": rec["officers"],
                        "recommended_barricades": rec["barricades"],
                        "recommended_diversion_required": rec["diversion_required"],
                        "recommended_diversion_plan": rec["diversion"],
                        "actual_clearance_mins": actual_time,
                        "actual_officers_used": actual_officers,
                        "actual_barricades_used": actual_barricades,
                        "actual_diversion_required": actual_diversion_required,
                        "prediction_feedback": was_prediction_accurate,
                        "observed_field_impact_score": observed_field_impact,
                        "impact_error": impact_error,
                        "notes": description_input
                    }

                    try:
                        saved_path = save_feedback_log(feedback_row, RETRAIN_LOG_FILE)
                        st.success("✅ Feedback logged successfully.")
                        st.info(f"Saved to: {saved_path}")
                        st.metric("Observed Field Impact Score", observed_field_impact)
                        st.metric("Impact Error (Observed - Predicted)", impact_error)
                    except Exception as e:
                        st.error(f"❌ Error saving feedback: {e}")

            st.markdown("### Saved Feedback History")
            log_df = load_retraining_log(RETRAIN_LOG_FILE)

            if not log_df.empty:
                st.dataframe(log_df, use_container_width=True)
                st.caption(f"Current log file: {os.path.abspath(RETRAIN_LOG_FILE)}")
            else:
                st.info("No retraining log found yet. Submit one feedback record first.")

    else:
        st.info("👈 Fill the incident details in the sidebar and click **Analyze Incident**.")

# ============================================================
# PAGE 3: HOTSPOT INTELLIGENCE
# ============================================================

elif page == "Hotspot Intelligence":

    st.subheader("Historical Hotspot Intelligence")

    st.markdown(
        """
        This module highlights historical junction-level traffic hotspots derived from
        event frequency and Traffic Impact Index patterns.
        """
    )

    hotspot_display = hotspots[
        ["junction", "event_count", "avg_impact", "risk_level"]
    ].copy()

    hotspot_display.columns = [
        "Junction",
        "Events",
        "Traffic Impact Index",
        "Risk Level"
    ]

    st.dataframe(hotspot_display.head(30), use_container_width=True)

    st.markdown("---")
    st.subheader("Interactive Hotspot Map")

    if os.path.exists("traffic_hotspots_final.html"):
        with open("traffic_hotspots_final.html", "r", encoding="utf-8") as f:
            map_html = f.read()

        components.html(
            map_html,
            height=750,
            scrolling=True
        )
    else:
        st.warning("⚠️ `traffic_hotspots_final.html` not found in the project folder.")

# ============================================================
# PAGE 4: EVENT ANALYTICS
# ============================================================

elif page == "Event Analytics":

    st.subheader("Event Analytics & Operational Patterns")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.markdown("### Event Cause Distribution")
        cause_df = df["event_cause"].value_counts().reset_index()
        cause_df.columns = ["Event Cause", "Count"]

        fig = px.bar(
            cause_df.head(15),
            x="Event Cause",
            y="Count",
            title="Event Cause Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.markdown("### Priority Distribution")
        priority_df = df["priority"].value_counts().reset_index()
        priority_df.columns = ["Priority", "Count"]

        fig = px.pie(
            priority_df,
            names="Priority",
            values="Count",
            title="Priority Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown("### Planned vs Unplanned Events")
        type_df = df["event_type"].value_counts().reset_index()
        type_df.columns = ["Event Type", "Count"]

        fig = px.bar(
            type_df,
            x="Event Type",
            y="Count",
            title="Planned vs Unplanned Events"
        )
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.markdown("### Top Police Stations by Event Volume")
        if "police_station" in df.columns:
            ps_df = (
                df["police_station"]
                .value_counts()
                .reset_index()
                .head(10)
            )
            ps_df.columns = ["Police Station", "Count"]

            fig = px.bar(
                ps_df,
                x="Police Station",
                y="Count",
                title="Top Police Stations"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("### Junction Hotspot Summary")
    hotspot_summary = hotspots[
        ["junction", "event_count", "avg_impact", "risk_level"]
    ].head(20).copy()

    hotspot_summary.columns = [
        "Junction",
        "Events",
        "Traffic Impact Index",
        "Risk Level"
    ]

    st.dataframe(hotspot_summary, use_container_width=True)