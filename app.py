import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mój Portfel", page_icon="📈", layout="wide")

st.title(" Portfel Inwestycyjny")
st.caption("Test aplikacji")

data = {
    "Narzędzie": ["Obligacje", "Akcje"],
    "Kwota inwestycji [PLN]": [10000, 27077.72],
    "Obecna wartość [PLN]": [10442, 28355.00],
}
df = pd.DataFrame(data)
df["Zysk [PLN]"] = df["Obecna wartość [PLN]"] - df["Kwota inwestycji [PLN]"]
df["Zwrot %"] = (df["Zysk [PLN]"] / df["Kwota inwestycji [PLN]"]) * 100

st.subheader("Podsumowanie (na sztywno, demo)")
st.dataframe(df, use_container_width=True)

total_invested = df["Kwota inwestycji [PLN]"].sum()
total_value = df["Obecna wartość [PLN]"].sum()
total_profit = total_value - total_invested
total_return_pct = (total_profit / total_invested) * 100

left, right = st.columns(2)
with left:
    st.metric("Łączna kwota inwestycji", f"{total_invested:,.2f} PLN")
    st.metric("Obecna wartość", f"{total_value:,.2f} PLN")
with right:
    st.metric("Zysk łączny", f"{total_profit:,.2f} PLN")
    st.metric("Zwrot %", f"{total_return_pct:,.2f}%")