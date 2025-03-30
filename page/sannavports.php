<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirect in corso...</title>
    <link rel="stylesheet" href="static/css/bootstrap.min.css">

    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #ffff00, #ffffff);
        }
        .redirect-box {
            text-align: center;
            background: linear-gradient(180deg, #e40303, #ff8c00, #ffed00, #008026, #24408e, #732982);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
    </style>
    <script>
        setTimeout(function() {
            window.location.href = "http://" + window.location.hostname + ":5001/";
        }, 3000); // Redirect dopo 3 secondi
    </script>
</head>
<body>
    <div class="redirect-box">
        <h3>Reindirizzamento in corso...</h3>
        <p>Attendi un momento e aggiorna il bookmark, stiamo portandoti alla nuova destinazione.</p>
        <p>Abbiamo introdotto l'uso di sqlite per migliorare le performance.</p>
        <p>Direi che ci siamo riusciti!!! Dicci la tua opinione:
           <a href="mailto:axxxa54@gmail.com">Axxx</a>
        </p>
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Se il reindirizzamento non avviene, <a href="#" onclick="window.location.href = 'http://' + window.location.hostname + ':5001/'">clicca qui</a>.</p>
    </div>
</body>
</html>
