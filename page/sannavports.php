<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>All Ports</title>
  <link rel="icon" href="favicon.ico" />
  <!-- Bootstrap CSS -->
  <link rel="stylesheet" href="static/css/bootstrap.min.css">
  <!-- DataTables CSS -->
  <link rel="stylesheet" href="static/css/dataTables.bootstrap4.min.css">
  <link rel="stylesheet" href="style.css">
</head>
<body>
   <!-- Loader -->
   <div id="loader" class="loading-overlay text-center">
      <div class="spinner-border text-primary" role="status"></div>
      <p>Caricamento dati...</p>
   </div>

   <div class="container-fluid full-page">
      <!-- Header -->
      <div class="row">
         <div class="col-12 page-header">
            <h1 class="display-3 font-weight-bold text-primary">All Ports</h1>
         </div>
      </div>

      <div class="container-fluid d-flex justify-content-between align-items-center mb-3">

      <!-- Sezione Ultimo aggiornamento -->
      <div class="update-time text-left">
         <strong>Ultimo aggiornamento:</strong>
         <?php
            date_default_timezone_set('Europe/Rome');
            $filePath = 'result_json/output.csv.gz';
            if (file_exists($filePath)) {
               echo date("d-m-Y H:i:s", filemtime($filePath));
            } else {
               echo "Il file non esiste.";
            }
         ?>
      </div>

      <!-- Sezione Bottoni Export -->
      <div class="export-buttons">
           <button id="exportCSV" class="btn btn-primary">Export to CSV</button>
           <button id="exportXLS" class="btn btn-success">Export to XLS</button>
       </div>
   </div>


   <!-- Sezione per il controllo della visibilità delle colonne -->
   <div class="column-toggle">
      <strong>Mostra/Nascondi colonne:</strong>
      <span id="columnToggles"></span>
   </div>

   <div class="row table-container">
      <div class="col-12">
         <div class="table-responsive">
            <table id="csvTable" class="table table-striped table-bordered" style="width:100%;">
               <thead>
                  <tr id="tableHeader">
                     <!-- Le intestazioni verranno generate dinamicamente -->
                 </tr>
               </thead>
               <tbody id="tableBody">  <!-- Le righe del CSV verranno inserite qui --> </tbody>
            </table>
         </div>
      </div>
   </div>

   <!-- jQuery -->
   <script src="static/js/jquery-3.5.1.min.js"></script>
   <!-- Bootstrap JS -->
   <script src="static/js/bootstrap.bundle.min.js"></script>
   <!-- DataTables JS -->
   <script src="static/js/jquery.dataTables.min.js"></script>
   <script src="static/js/dataTables.bootstrap4.min.js"></script>
   <!-- PapaParse per il parsing del CSV -->
   <script src="static/js/papaparse.min.js"></script>
   <!-- FileSaver.js per il salvataggio dei file -->
   <script src="static/js/FileSaver.min.js"></script>

   <script>
   console.log("Il file JS sta eseguendo!");
   //$(document).ready(function() {
   //    console.log("jQuery document ready!");
   //});

   $(document).ready(function() {
      //console.log("Pagina caricata, avvio il loader...");
      $("#loader").show();

      // Carica e processa il CSV.gz
      fetch("result_json/output.csv.gz")
        .then(response => response.text())
        .then(csvData => {
        Papa.parse(csvData, {
            skipEmptyLines: true,
            header: true,
            complete: function(results) {
               console.log("Parsing completato, numero di righe:", results.data.length);
               var data = results.data;
               var headers = results.meta.fields;

               // Costruisci la riga delle intestazioni
               var headerRow = '';
               headers.forEach(function(header) {
                  headerRow += "<th>" + header + "</th>";
               });
               $("#tableHeader").html(headerRow);
               console.log("Intestazioni inserite:", headers);

               // Crea la riga per i campi di ricerca
               var searchRow = $('<tr></tr>').appendTo('#csvTable thead');
               headers.forEach(function(header, i) {
                  var th = $('<th></th>');
                  if (!["ZONE", "RESULT_JSON", "STATE", "STATUS"].includes(header)) {
                     th.html('<input type="text" placeholder="Cerca ' + header + '" />');
                  }
                  th.find('input').on('keyup change', function() {
                     if (table.column(i).search() !== this.value) {
                        table.column(i).search(this.value).draw();
                     }
                  });
                  searchRow.append(th);
               });

               // Inserisci i dati nella tabella
               data.forEach(function(row) {
                  var tr = "<tr>";
                  headers.forEach(function(header) {
                     tr += "<td>" + row[header] + "</td>";
                  });
                  tr += "</tr>";
                  $("#tableBody").append(tr);
               });

               // Inizializza DataTable
               var table = $('#csvTable').DataTable({
                  orderCellsTop: true,
                  fixedHeader: true,
                  pageLength: 50,
                  language: { search: "Ricerca globale:" },
                  columnDefs: [
                     { targets: headers.indexOf("STATUS"), visible: false },
                     { targets: headers.indexOf("STATE"), visible: false },
                     { targets: headers.indexOf("ZONE"), visible: false },
                     { targets: headers.indexOf("RESULT_JSON"), visible: false }
                  ]
               });

               // Genera i controlli per mostrare/nascondere le colonne
               headers.forEach(function(header, index) {
                  var isVisible = !(header === "ZONE" || header === "RESULT_JSON" || header === "STATE" || header === "STATUS");

                  $('#columnToggles').append(`
                     <label>
                        <input type="checkbox" class="toggle-col" data-column="${index}" ${isVisible ? 'checked' : ''}>
                        ${header}
                     </label>
                  `);
               });

               // Cambia il numero di righe per pagina
               $('#pageLength').on('change', function() {
                  var pageLength = $(this).val();
                  table.page.len(pageLength).draw();
               });

               // Aggiungi evento per il toggle delle colonne
               $('.toggle-col').on('change', function() {
                  var columnIndex = $(this).data('column');
                  var column = table.column(columnIndex);
                  column.visible(!column.visible());
                  table.columns.adjust().draw();

                  // Se la colonna è ora visibile, aggiungi l'input di ricerca
                  var searchTh = $('#csvTable thead tr:eq(1) th').eq(columnIndex);
                  if (column.visible() && !searchTh.find('input').length) {
                     searchTh.html('<input type="text" placeholder="Cerca ' + headers[columnIndex] + '" />');
                     searchTh.find('input').on('keyup change', function() {
                        if (table.column(columnIndex).search() !== this.value) {
                           table.column(columnIndex).search(this.value).draw();
                        }
                     });
                  }
               });

               console.log("Tabella generata con successo!");
               $("#loader").fadeOut();
            }
        });
      });
   });
   </script>

</body>
</html>
