from __future__ import annotations
import datetime as dt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Gestion des Réservations – Prédiction d'Annulations",
    page_icon="🏨",
    layout="wide",
)


st.title("🏨 Enregistrement de Réservation – Manager")
st.caption("Complétez le formulaire comme lors d'une saisie client; le modèle va ensuite ensuite prédire si le client annule ou pas.")


with st.form("booking_form", clear_on_submit=False):

    # Détails du séjour 
    st.markdown("### Détails du Séjour")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        hotel = st.selectbox("Établissement", ["Resort Hotel", "City Hotel"])

    with col_b:
        arrival_date = st.date_input(
            "Date d'arrivée",
            value=dt.date.today() + dt.timedelta(days=30),
        )

    with col_c:
        nights_total = st.number_input(
            "Nombre total de nuits", min_value=1, value=1, step=1
        )

    departure_date: dt.date = arrival_date + dt.timedelta(days=int(nights_total))
    st.write(f"**Date de départ calculée :** {departure_date.strftime('%d %B %Y')}")

    col_we, col_wd = st.columns(2)
    stays_in_weekend_nights = col_we.number_input("Nuits week‑end", min_value=0, value=0, step=1)
    stays_in_week_nights = col_wd.number_input(
        "Nuits semaine", min_value=0, value=int(nights_total) - stays_in_weekend_nights, step=1
    )

    # Occupants
    st.markdown("### Occupants")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    adults = col1.number_input("Adultes", min_value=1, value=2, step=1)
    children = col2.number_input("Enfants", min_value=0, value=0, step=1)
    babies = col3.number_input("Bébés", min_value=0, value=0, step=1)
    is_repeated_guest = col4.checkbox("Client récurrent ?", value=False)

    #  Chambre & Tarif 
    st.markdown("### Chambre & Tarif")
    colr1, colr2, colr3 = st.columns(3)
    room_letters = list("ABCDEFGH")  

    reserved_room_type = colr1.selectbox("Type de chambre réservée", room_letters, index=2)
    assigned_room_type = colr2.selectbox("Type de chambre assignée", room_letters, index=2)

    adr = colr3.number_input("Tarif Moyen (ADR €)", min_value=0.0, value=95.0, step=0.1)
    adr_q = st.radio("Quartile ADR", ["Q1", "Q2", "Q3", "Q4"], horizontal=True)

    # Canaux & Conditions
    st.markdown("### Canaux & Conditions")
    colc1, colc2 = st.columns(2)

    with colc1:
        market_segment = st.selectbox(
            "Segment de marché",
            [
                "Direct",
                "Corporate",
                "Online TA",
                "Offline TA/TO",
                "Complementary",
            ],
        )
        distribution_channel = st.selectbox(
            "Canal de distribution", ["Direct", "TA/TO", "Corporate", "GDS"]
        )
        deposit_type = st.selectbox(
            "Type de dépôt", ["No Deposit", "Refundable", "Non Refund"]
        )

    with colc2:
        customer_type = st.selectbox(
            "Type de client",
            ["Transient", "Contract", "Transient-Party", "Group"],
        )
        meal = st.selectbox("Formule repas", ["BB", "HB", "FB", "SC"])
        total_of_special_requests = st.number_input(
            "Demandes spéciales", min_value=0, value=0, step=1
        )

    #  Historique & Suivi
    st.markdown("### Historique & Suivi")
    colh1, colh2, colh3 = st.columns(3)

    booking_changes = colh1.number_input("Modifications", min_value=0, value=0, step=1)
    previous_cancellations = colh2.number_input("Annulations précédentes", min_value=0, value=0, step=1)
    previous_bookings_not_canceled = colh3.number_input(
        "Réservations précédentes non annulées", min_value=0, value=0, step=1
    )

    # Agents & Entreprises 
    st.markdown("### Agents & Entreprises")
    colae1, colae2, colae3 = st.columns(3)

    agent = colae1.text_input("Agent", value="inconnue")
    company = colae2.text_input("Société", value="inconnue")
    country = colae3.text_input("Pays (ISO)", value="PRT").upper()

    # Soumission 
    submitted = st.form_submit_button("📊 Prédire le risque d'annulation")


if submitted:
    from classifier import classifier

    today = dt.date.today()
    lead_time = max((arrival_date - today).days, 0)

    arrival_date_day_of_month = arrival_date.day
    arrival_date_month = arrival_date.strftime("%B")
    arrival_date_week_number = arrival_date.isocalendar().week

    def categorize_lead_time(x: int) -> str:
        if x <= 7:
            return "≤7 j"
        if x <= 30:
            return "8-30 j"
        if x <= 60:
            return "31-60 j"
        if x <= 180:
            return "61-180 j"
        return "≥181 j"

    def categorize_booking_changes(x: int) -> str:
        return "≥2" if x >= 2 else "<2"

    lead_bin = categorize_lead_time(lead_time)
    chg_bin = categorize_booking_changes(booking_changes)
    last_minute = lead_time <= 7

    data = {
        "adr": adr,
        "adr_q": adr_q,
        "adults": adults,
        "agent": agent or "inconnue",
        "arrival_date_day_of_month": arrival_date_day_of_month,
        "arrival_date_month": arrival_date_month,
        "arrival_date_week_number": arrival_date_week_number,
        "assigned_room_type": assigned_room_type,
        "babies": babies,
        "booking_changes": booking_changes,
        "chg_bin": chg_bin,
        "children": children,
        "company": company or "inconnue",
        "country": country or "PRT",
        "customer_type": customer_type,
        "deposit_type": deposit_type,
        "distribution_channel": distribution_channel,
        "hotel": hotel,
        "is_repeated_guest": int(is_repeated_guest),
        "last_minute": last_minute,
        "lead_bin": lead_bin,
        "lead_time": lead_time,
        "market_segment": market_segment,
        "meal": meal,
        "previous_bookings_not_canceled": previous_bookings_not_canceled,
        "previous_cancellations": previous_cancellations,
        "reserved_room_type": reserved_room_type,
        "stays_in_week_nights": stays_in_week_nights,
        "stays_in_weekend_nights": stays_in_weekend_nights,
        "total_of_special_requests": total_of_special_requests,
    }

    df = pd.DataFrame([data])

    try:
        raw_result = classifier(df)
        if isinstance(raw_result, tuple):
            classe, proba = raw_result
        else:
            classe, proba = raw_result, None

        st.subheader("Résultat de la Prédiction")
        if proba is not None:
            st.success(f"Classe : **{classe}** – Probabilité {proba:.0%}")
            st.progress(int(proba * 100))
        else:
            st.success(f"Classe : **{classe}**")


    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
