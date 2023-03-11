GENERIC_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
        }
        h1, div {
            background: rgb(218, 218, 218);
            text-align: center;
            padding: 10px;
            margin: 0;
        }
        p {
            background-color: rgb(245, 245, 245);
            margin: 0;
            padding: 10px;
            text-align: center;
        }
        a {
            display: block;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>
        TITLE
    </h1>
    <p>Olá, USER_NAME! Tivemos um problema no envio de email da nossa aplicação:
    SERVICE_NAME, mas a StartNow, que gerencia este serviço, cuidou para que tudo
    corresse bem. Você realizou a função de: ACTION e aqui está o seu link:</p>
    <a target="_blank" href="LINK">LINK</a>
    <div>
        StartNow. CNPJ: 45.453.667/0001-88
    </div>
</body>
</html>
"""
