<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Ricerca WWPN</title>
  <link rel="icon" href="favicon.ico" />
  <link rel="stylesheet" href="static/css/bootstrap.min.css">
  <style>
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
      background-color: #f8f9fa;
    }
    .container-fluid {
      height: 100%;
      padding: 20px;
    }
    table {
      background-color: #fff;
      width: 100%;
    }
    .toggle-details {
      background-color: #e9ecef;
      display: none;
    }
    .highlight {
      background-color: #ffeeba;
      cursor: pointer;
    }
    .input-group {
      max-width: 100%;
    }
    .table-responsive {
      height: calc(100% - 180px);
      overflow-y: auto;
    }
  </style>
</head>

<body>
  <div class="container-fluid">
    <h1 class="display-4 text-primary">Ricerca WWPN</h1>

    <form method="get" class="my-4">
      <div class="input-group">
        <input type="text" name="wwpn" class="form-control" placeholder="Inserisci uno o più WWPN separati da spazi" required>
        <div class="input-group-append">
          <button type="submit" class="btn btn-primary">Cerca</button>
        </div>
      </div>
    </form>

    <?php
      if (isset($_GET['wwpn']) && !empty(trim($_GET['wwpn']))) {
        $searchWWPNs = preg_split('/\s+/', trim($_GET['wwpn']));
        $searchWWPNs = array_map('strtolower', $searchWWPNs);

        echo "<div class='mb-3'><strong>Ricerca per:</strong> " . implode(", ", $searchWWPNs) . "</div>";

        $filePath = 'result_json/output.csv.gz';
        if (file_exists($filePath)) {
          $handle = gzopen($filePath, 'r');
          if ($handle) {
            $headers = str_getcsv(gzgets($handle));
            $zoneIndex = array_search('ZONE', $headers);
            $noteIndex = array_search('NOTE', $headers);

            echo "<div class='table-responsive'><table class='table table-bordered table-striped'>";
            echo "<thead><tr>";
            foreach ($headers as $index => $header) {
              if ($header !== 'ZONE' && $header !== 'NOTE') {
                echo "<th>$header</th>";
              }
            }
            echo "</tr></thead><tbody>";

            $found = false;
            $rowId = 0;
            while (($line = gzgets($handle)) !== false) {
              $row = str_getcsv($line);
              $rowLower = array_map('strtolower', $row);
              $wwpnMatched = false;

              foreach ($rowLower as $value) {
                foreach ($searchWWPNs as $wwpn) {
                  if (strpos($value, $wwpn) !== false) {
                    $wwpnMatched = true;
                    break 2;
                  }
                }
              }

              if ($wwpnMatched) {
                $found = true;
                $zone = $zoneIndex !== false ? htmlspecialchars($row[$zoneIndex]) : 'N/A';
                $note = $noteIndex !== false ? htmlspecialchars($row[$noteIndex]) : 'N/A';

                // Riga principale cliccabile
                echo "<tr class='highlight' data-toggle='details$rowId'>";
                foreach ($row as $index => $cell) {
                  if ($headers[$index] !== 'ZONE' && $headers[$index] !== 'NOTE') {
                    echo "<td>" . htmlspecialchars($cell) . "</td>";
                  }
                }
                echo "</tr>";

                // Riga nascosta con ZONE e NOTE
                echo "<tr class='toggle-details' id='details$rowId'><td colspan='" . (count($headers) - 2) . "'>";
                echo "<strong>ZONE:</strong> $zone<br><strong>NOTE:</strong> $note";
                echo "</td></tr>";

                $rowId++;
              }
            }

            echo "</tbody></table></div>";

            if (!$found) {
              echo "<div class='alert alert-warning'>Nessun risultato trovato.</div>";
            }

            gzclose($handle);
          } else {
            echo "<div class='alert alert-danger'>Errore nell'aprire il file.</div>";
          }
        } else {
          echo "<div class='alert alert-danger'>File CSV non trovato.</div>";
        }
      }
    ?>
  </div>

  <script src="static/js/bootstrap.bundle.min.js"></script>
  <script src="static/js/jquery-3.5.1.min.js"></script>
  <script>
    $(document).ready(function() {
      $('.highlight').on('click', function() {
        var target = '#' + $(this).data('toggle');
        $(target).slideToggle();
      });
    });
  </script>
</body>
</html>
