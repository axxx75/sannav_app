<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALL_ALIAS</title>
    <style>
        body {
            background-color: yellow;
            font-family: courier;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>ALL_ALIAS</h1>
    <?php
        // Imposta il percorso del file CSV compresso
        $csvFile = '/var/www/localhost/htdocs/result_json/output.csv.gz';

        // Apri il file CSV compresso
        $handle = gzopen($csvFile, 'r');

        if ($handle) {
            // Legge il contenuto del file
            $content = stream_get_contents($handle);

            // Chiudi il file
            gzclose($handle);

            // Stampa il contenuto del file
            echo '<pre>'. htmlspecialchars($content, ENT_QUOTES, 'UTF-8'). '</pre>';
        } else {
            echo 'Errore: non è stato possibile aprire il file CSV.';
        }
   ?>
</body>
</html>
