FROM python:3.11
ENV VENV_PATH="/venv"
ENV PATH="$VENV_PATH/bin:$PATH"
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils && \
    apt-get upgrade -y && \
    apt-get install pandoc texlive-latex-base texlive-latex-extra zip -y && \
    apt-get autoclean
RUN python -m venv /venv
COPY . .
RUN /venv/bin/pip install --upgrade pip wheel setuptools &&\
    /venv/bin/pip install -r requirements.txt
EXPOSE 80
CMD streamlit run app.py --server.port 80