from api_app import init_app

app = init_app()
if __name__ == '__main__':
    app.run(host='api-tvprogram.rhcloud.com', port=8080)
