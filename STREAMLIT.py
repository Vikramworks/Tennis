import streamlit as st
import mysql.connector
import pandas as pd

# Database connection details
host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
user = "3HnrAoXYB1zUtgp.root"
password = "t6By7FBUzVuxXJ1W"
database = "tennisdata"
port = 4000

# Function to connect to the database
def create_connection():
    return mysql.connector.connect(
        host=host, user=user, password=password, database=database, port=port
    )

# Function to fetch all table names
def get_table_names():
    conn = None
    try:
        conn = create_connection()
        query = "SHOW TABLES"
        tables = pd.read_sql(query, conn)
        return tables.iloc[:, 0].tolist()  # Extract table names
    except Exception as e:
        st.error(f"Error fetching table names: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()
def fetch_summary_statistics():
    conn = None
    try:
        conn = create_connection()
        
        # SQL queries to fetch summary statistics
        total_competitors_query = "SELECT COUNT(*) AS total_competitors FROM competitor"
        total_countries_query = "SELECT COUNT(DISTINCT country) AS total_countries FROM competitor"
        highest_points_query = "SELECT MAX(points) AS highest_points FROM competitor_rankings"
        
        total_competitors = pd.read_sql(total_competitors_query, conn).iloc[0, 0]
        total_countries = pd.read_sql(total_countries_query, conn).iloc[0, 0]
        highest_points = pd.read_sql(highest_points_query, conn).iloc[0, 0]
        
        return total_competitors, total_countries, highest_points
        
    except Exception as e:
        st.error(f"Error fetching summary statistics: {e}")
        return None, None, None
    finally:
        if conn and conn.is_connected():
            conn.close()            

# Home Page
import streamlit as st
import pandas as pd

def home_page():
    st.title("TENNIS DATA ANALYSIS")
    st.image(
        "https://img.freepik.com/premium-photo/park-with-tennis-courts_1234738-204771.jpg",
        use_container_width=True,
        caption="Welcome to the Tennis Data Analysis App"
    )

    # Fetch summary statistics
    total_competitors, total_countries, highest_points = fetch_summary_statistics()

    if total_competitors is not None and total_countries is not None and highest_points is not None:
        st.subheader("Summary Statistics")
        st.write(f"Total number of competitors: {total_competitors}")
        st.write(f"Number of countries represented: {total_countries}")
        st.write(f"Highest points scored by a competitor: {highest_points}")
    
    # Rank filters and competitors display
    st.subheader("View Competitors by Rank")
    rank_start = st.number_input("Start Rank", min_value=1, step=1, value=1, key="rank_start")
    rank_end = st.number_input("End Rank", min_value=1, step=1, value=5, key="rank_end")
    
    if st.button("Show Competitors"):
        conn = None
        try:
            conn = create_connection()
            query = f"""
            SELECT c.name AS Competitor_Name, cr.`rank` AS `Rank`, cr.points AS Points
            FROM competitor_rankings cr
            JOIN competitor c ON cr.competitor_id = c.competitor_id
            WHERE cr.`rank` BETWEEN {rank_start} AND {rank_end}
            ORDER BY cr.`rank` ASC;
            """     
            df = pd.read_sql(query, conn)
            st.write(f"Competitors Ranked Between {rank_start} and {rank_end}:")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching competitors: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    st.write("Use the sidebar to navigate between pages and explore tennis-related data.")

    # Dropdown for selecting country
    st.subheader("View Competitors by Country")
    countries = ["USA", "Japan", "Peru", "Burundi", "Russia", "Jamaica", "Latvia", "Italy", "Poland", "Great Britain"]
    selected_country = st.selectbox("Select a country", countries)

    if st.button("Show Competitors by Country"):
        conn = None
        try:
            conn = create_connection()
            query = f"""
            SELECT c.country, cr.rank, cr.points, c.name
            FROM competitor AS c
            JOIN competitor_rankings AS cr ON c.competitor_id = cr.competitor_id
            WHERE c.country = '{selected_country}'
            ORDER BY cr.rank ASC;
            """
            
            df = pd.read_sql(query, conn)
            st.write(f"Competitors from {selected_country}:")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching competitors for {selected_country}: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    # Dropdown for selecting name
    st.subheader("View Competitors by Name ")
    Name = [
        "Sachko, Vitaliy",
        "Turker, Mert Naci",
        "Bolkvadze, Mariam",
        "Rybakov, Alex",
        "Huang, Yujia",
        "Trhac, Patrik",
        "Pawlikowska, Zuzanna",
        "Tabilo, Alejandro",
        "Van de Zandschulp, Botic"
    ]

    selected_name = st.selectbox("Select a Name ", Name)

    if st.button("Show Competitors by Name"):
        conn = None
        try:
            conn = create_connection()
            query = f"""
            SELECT c.country, cr.rank, cr.points, c.name
            FROM competitor AS c
            JOIN competitor_rankings AS cr ON c.competitor_id = cr.competitor_id
            WHERE c.name = '{selected_name}'
            ORDER BY cr.rank ASC;
            """
            df = pd.read_sql(query, conn)
            st.write(f"Competitors for {selected_name}:")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching competitors for {selected_name}: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()


# Complex & Venues Page
def complex_page():
    st.title("Complex & Venues")
    st.image(
        "https://www.2playbook.com/uploads/s1/13/54/9/godo-torneo-tenis-barcelona.jpeg",
        use_container_width=True,
        caption="Real Club de Denis Barcelona "
    )
    st.title("Real Club de Denis Barcelona Have More Ports ")

    
    # Dynamic Data Filters
    st.sidebar.subheader("Data Filters")
    
    # Fetch table names and filter for Complex & Venues
    table_names = get_table_names()
    filtered_tables = [table for table in table_names if table.lower() in ["complexes", "venues"]]
    
    if filtered_tables:
        # Dropdown to select a table
        selected_table = st.sidebar.selectbox("Select table to view", filtered_tables)
        
        # Button to view table data
        if st.sidebar.button("Show Table Data"):
            conn = None
            try:
                conn = create_connection()
                query = f"SELECT * FROM {selected_table} LIMIT 100"  # Fetch first 100 rows
                df = pd.read_sql(query, conn)
                st.write(f"Data from table: {selected_table}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching data: {e}")
            finally:
                if conn and conn.is_connected():
                    conn.close()

    else:
        st.sidebar.warning("No tables found for Complex & Venues.")

    # Sidebar for query execution selection
    st.sidebar.subheader("Execute Specific Queries")
    query_choice = st.sidebar.selectbox(
        "Select a query to execute",
        [
            "List all venues along with their associated complex name",
            "Count the number of venues in each complex",
            "Get details of venues in a specific country (e.g., Chile)",
            "Identify all venues and their timezones",
            "Find complexes that have more than one venue",
            "List venues grouped by country",
            "Find all venues for a specific complex (e.g., Nacional)",
        ]
    )

    # Inputs for specific queries
    country = None
    complex_name = None
    if query_choice == "Get details of venues in a specific country (e.g., Chile)":
        country = st.sidebar.text_input("Enter the country name:", "Chile")
    if query_choice == "Find all venues for a specific complex (e.g., Nacional)":
        complex_name = st.sidebar.text_input("Enter the complex name:", "Nacional")

    # Button to execute query
    if st.sidebar.button("Execute Query"):
        conn = None
        try:
            conn = create_connection()

            # Define queries
            queries = {
                "List all venues along with their associated complex name": """
                    SELECT venues.venue_name AS Venue, complexes.complex_name AS Complex
                    FROM venues
                    JOIN complexes ON venues.complex_id = complexes.complex_id
                """,
                "Count the number of venues in each complex": """
                    SELECT complexes.complex_name AS Complex, COUNT(venues.venue_id) AS Venue_Count
                    FROM venues
                    JOIN complexes ON venues.complex_id = complexes.complex_id
                    GROUP BY complexes.complex_name order by venue_count desc
                """,
                "Get details of venues in a specific country (e.g., Chile)": f"""
                    SELECT * FROM venues
                    WHERE country_name = '{country}';
                """ if country else "",
                "Identify all venues and their timezones": """
                    SELECT venue_name AS Venue, timezone AS Timezone
                    FROM venues;
                """,
                "Find complexes that have more than one venue": """
                    SELECT complexes.complex_name AS Complex, COUNT(venues.venue_id) AS Venue_Count
                    FROM venues
                    JOIN complexes ON venues.complex_id = complexes.complex_id
                    GROUP BY complexes.complex_name
                    HAVING Venue_Count > 1
                """,
                "List venues grouped by country": """
                    SELECT country_name AS Country, GROUP_CONCAT(venue_name SEPARATOR ', ') AS Venues
                    FROM venues
                    GROUP BY country_name
                """,
                "Find all venues for a specific complex (e.g., Nacional)": f"""
                    SELECT venues.venue_name AS Venue
                    FROM venues
                    JOIN complexes ON venues.complex_id = complexes.complex_id
                    WHERE complexes.complex_name = '{complex_name}';
                """ if complex_name else ""
            }

            # Get the selected query
            query = queries.get(query_choice, "")
            if query:
                # Execute the query
                df = pd.read_sql(query, conn)
                st.write(f"Results for: {query_choice}")
                st.dataframe(df)
            else:
                st.error("Invalid query or missing input.")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()

# Competitions Page
def competitions_page():
    st.title("Competitions")
    st.image(
        "https://cdn.theathletic.com/app/uploads/2024/04/28080614/Rohan-Bopanna-Qureshi-scaled-e1714306045153.jpg",
        use_container_width=True,
        caption="Doubles Competitions")
    # Fetch table names and filter for Competitions (competitions and category)
    table_names = get_table_names()
    filtered_tables = [table for table in table_names if table.lower() in ["competitions", "category"]]
    
    if filtered_tables:
        # Dropdown to select a table
        selected_table = st.sidebar.selectbox("Select table to view", filtered_tables)
        
        # Button to view table data
        if st.sidebar.button("Show Table Data"):
            conn = None
            try:
                conn = create_connection()
                query = f"SELECT * FROM {selected_table} LIMIT 100"  # Fetch first 100 rows
                df = pd.read_sql(query, conn)
                st.write(f"Data from table: {selected_table}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching data: {e}")
            finally:
                if conn and conn.is_connected():
                    conn.close()

    else:
        st.sidebar.warning("No tables found for Competitions.")

    # Sidebar for query execution selection
    st.sidebar.subheader("Execute Specific Queries")
    query_choice = st.sidebar.selectbox(
        "Select a query to execute",
        [
            "List all competitions along with their category name",
            "Count the number of competitions in each category",
            "Find all competitions of type 'doubles'",
            "Get competitions that belong to a specific category (e.g., ITF Men)",
            "Identify parent competitions and their sub-competitions",
            "Analyze the distribution of competition types by category",
            "List all competitions with no parent (top-level competitions)"
        ]
    )

    # Inputs for specific queries
    category_name = None
    if query_choice == "Get competitions that belong to a specific category (e.g., ITF Men)":
        category_name = st.sidebar.text_input("Enter the category name:", "ITF Men")

    # Button to execute query
    if st.sidebar.button("Execute Query"):
        conn = None
        try:
            conn = create_connection()

            # Define queries
            queries = {
                "List all competitions along with their category name": """
                    SELECT competitions.competition_name AS Competition, category.category_name AS Category
                    FROM competitions
                    JOIN category ON competitions.category_id = category.category_id
                """,
                "Count the number of competitions in each category": """
                    SELECT category.category_name AS Category, COUNT(competitions.competition_id) AS Competition_Count
                    FROM competitions
                    JOIN category ON competitions.category_id = category.category_id
                    GROUP BY category.category_name
                """,
                "Find all competitions of type 'doubles'": """
                    SELECT competition_name
                    FROM competitions
                    WHERE type = 'doubles';
                """,
                "Get competitions that belong to a specific category (e.g., ITF Men)": f"""
                    SELECT competition_name
                    FROM competitions
                    WHERE category_id = (SELECT category_id FROM category WHERE category_name = '{category_name}')
                """ if category_name else "",
                "Identify parent competitions and their sub-competitions": """
                    SELECT parent_competition.competition_name AS Parent, sub_competition.competition_name AS Sub_Competition
                    FROM competitions AS parent_competition
                    JOIN competitions AS sub_competition ON parent_competition.competition_id = sub_competition.parent_id
                """,
                "Analyze the distribution of competition types by category": """
                    SELECT category.category_name AS Category, competitions.type AS Type, COUNT(*) AS Count
                    FROM competitions
                    JOIN category ON competitions.category_id = category.category_id
                    GROUP BY category.category_name, competitions.type
                """,
                "List all competitions with no parent (top-level competitions)": """
                    SELECT competition_name
                    FROM competitions
                    WHERE parent_id IS NULL;
                """
            }

            # Get the selected query
            query = queries.get(query_choice, "")
            if query:
                # Execute the query
                df = pd.read_sql(query, conn)
                st.write(f"Results for: {query_choice}")
                st.dataframe(df)
            else:
                st.error("Invalid query or missing input.")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()

# Competitor & Rankings Page
def competitor_rankings_page():
    st.title("Competitor & Rankings")
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/1/1b/Pavic_M._RG18_%287%29_%2842978774551%29.jpg",
        use_container_width=True,
        caption="Top Ranker"
    )
    st.title("Pavic Mate Top Ranker ")
    
    # Fetch table names and filter for Competitor & Rankings (competitor and competitor_rankings)
    table_names = get_table_names()
    filtered_tables = [table for table in table_names if table.lower() in ["competitor", "competitor_rankings"]]
    
    if filtered_tables:
        # Dropdown to select a table
        selected_table = st.sidebar.selectbox("Select table to view", filtered_tables)
        
        # Button to view table data
        if st.sidebar.button("Show Table Data"):
            conn = None
            try:
                conn = create_connection()
                query = f"SELECT * FROM {selected_table} LIMIT 100"  # Fetch first 100 rows
                df = pd.read_sql(query, conn)
                st.write(f"Data from table: {selected_table}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching data: {e}")
            finally:
                if conn and conn.is_connected():
                    conn.close()

    else:
        st.sidebar.warning("No tables found for Competitor & Rankings.")
    
    # Sidebar for query execution selection
    st.sidebar.subheader("Execute Specific Queries")
    query_choice = st.sidebar.selectbox(
        "Select a query to execute",
        [
            "Get all competitors with their rank and points",
            "Find competitors ranked in the top 5",
            "List competitors with no rank movement (stable rank)",
            "Get the total points of competitors from a specific country (e.g., Croatia)",
            "Count the number of competitors per country",
            "Find competitors with the highest points in the current week"
        ]
    )
    
    # Inputs for specific queries
    country = None
    if query_choice == "Get the total points of competitors from a specific country (e.g., Croatia)":
        country = st.sidebar.text_input("Enter the country name:", "Croatia")

    # Button to execute query
    if st.sidebar.button("Execute Query"):
        conn = None
        try:
            conn = create_connection()

            # Define queries
            queries = {
                "Get all competitors with their rank and points": """
                    SELECT c.name AS competitor_name, cr.rank, cr.points 
                    FROM competitor_rankings cr
                    JOIN competitor c ON cr.competitor_id = c.competitor_id
                    ORDER BY cr.rank ASC;
                
                """,
                "Find competitors ranked in the top 5": """
                    SELECT c.name AS competitor_name, cr.rank, cr.points 
                    FROM competitor_rankings cr
                    JOIN competitor c ON cr.competitor_id = c.competitor_id
                    WHERE cr.rank <= 5
                    ORDER BY cr.rank ASC;
                    
                    
                """,
                "List competitors with no rank movement (stable rank)": """
                    SELECT c.name AS competitor_name, cr.rank, cr.points 
                    FROM competitor_rankings cr
                    JOIN competitor c ON cr.competitor_id = c.competitor_id
                    WHERE cr.movement = 0;
                    
                    
                """,
                "Get the total points of competitors from a specific country (e.g., Croatia)": f"""
                       SELECT c.country, SUM(cr.points) AS total_points 
                       FROM competitor_rankings cr
                       JOIN competitor c ON cr.competitor_id = c.competitor_id
                       WHERE c.country = '{country}'
                       GROUP BY c.country;
                    
                    
                """ if country else "",
                "Count the number of competitors per country": """
                    SELECT c.country, COUNT(c.competitor_id) AS competitor_count 
                    FROM competitor c
                    GROUP BY c.country
                    ORDER BY competitor_count DESC;
                    
                    
                """,
                "Find competitors with the highest points in the current week": """
                    SELECT c.name AS competitor_name, cr.points 
                    FROM competitor_rankings cr
                    JOIN competitor c ON cr.competitor_id = c.competitor_id
                    WHERE cr.year = YEAR AND cr.week = WEEK
                    ORDER BY cr.points DESC 
                    LIMIT 5;
                    
                    
                    
                    
                """
            }

            # Get the selected query
            query = queries.get(query_choice, "")
            if query:
                # Execute the query
                df = pd.read_sql(query, conn)
                st.write(f"Results for: {query_choice}")
                st.dataframe(df)
            else:
                st.error("Invalid query or missing input.")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()

# Sidebar Navigation
st.sidebar.title("Tennis App Navigation")
selected_page = st.sidebar.radio(
    "Go to:",
    ["Home", "Competitions", "Competitor & Rankings", "Complex & Venues"]
)

# Page Routing
if selected_page == "Home":
    home_page()
elif selected_page == "Competitions":
    competitions_page()
elif selected_page == "Competitor & Rankings":
    competitor_rankings_page()
elif selected_page == "Complex & Venues":
    complex_page()
