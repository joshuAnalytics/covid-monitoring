mkdir -p ~/.streamlit/
mkdir -p ~/_data
mkdir -p ~/_data/daily/

echo "\
[general]\n\
email = \"jbramall@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml