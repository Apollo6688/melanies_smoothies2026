# Streamlit app for customizing smoothie orders
# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    # Build ingredients string once
    ingredients_string = ' '.join(ingredients_list)
    
    # Display nutrition info for selected fruits
    st.subheader("Nutrition Information")
    for fruit in ingredients_list:
        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"
            )
            smoothiefroot_response.raise_for_status()
            st.text(smoothiefroot_response.json())
        except requests.exceptions.RequestException as e:
            st.warning(f"Could not fetch nutrition info for {fruit}: {e}")
    
    # Submit button
    if st.button('Submit Order'):
        try:
            my_insert_stmt = "INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES (?, ?)"
            session.sql(my_insert_stmt, [ingredients_string, name_on_order]).collect()
            st.success("Order submitted successfully!")
        except Exception as e:
            st.error(f"Error submitting order: {e}")
