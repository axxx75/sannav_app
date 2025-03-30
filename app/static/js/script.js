document.addEventListener("DOMContentLoaded", function () {
    // Funzione per creare i checkbox per mostra/nascondi colonne
    window.initColumnSelectors = function(headers) {
        const columnSelectors = document.getElementById("columnSelectors");

        headers.forEach((header, index) => {
            // Crea il checkbox
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = true; // Di default tutte le colonne sono visibili
            checkbox.dataset.column = index;
            checkbox.addEventListener("change", toggleColumnVisibility);

            // Crea l'etichetta per il checkbox
            const label = document.createElement("label");
            label.textContent = " " + header;
            label.style.marginRight = "10px";

            columnSelectors.appendChild(checkbox);
            columnSelectors.appendChild(label);
        });
    };

    // Funzione per mostrare/nascondere colonne
    function toggleColumnVisibility(event) {
        const columnIndex = event.target.dataset.column;
        const th = document.querySelector(`th.col-${columnIndex}`); // Intestazione colonna
        const cells = document.querySelectorAll(`td.col-${columnIndex}`); // Celle della colonna

        if (event.target.checked) {
            th.style.display = ""; // Mostra la colonna
            cells.forEach(cell => cell.style.display = "");
        } else {
            th.style.display = "none"; // Nasconde la colonna
            cells.forEach(cell => cell.style.display = "none");
        }
    }
});

