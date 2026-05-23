import streamlit as st


def main():
    st.header("This is the title!")
    name = st.text_input("Enter your name")

    if st.button("Display name"):
        if name:
            st.write(f"Hello, {name}!")
        else:
            st.warning("Please enter your name first.")


if __name__ == "__main__":
    main()
