document.addEventListener("DOMContentLoaded", function () {
    const formsetContainer = document.querySelectorAll('.dynamic-invoiceitem_set');

    formsetContainer.forEach((form) => {
        const deleteCheckbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteCheckbox && !form.classList.contains('empty-form')) {
            // Hide the default delete checkbox
            deleteCheckbox.style.display = "none";

            // Create the ❌ delete button
            const deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.innerHTML = "❌";
            deleteBtn.title = "Delete this line item";
            deleteBtn.style.position = "absolute";
            deleteBtn.style.right = "10px";
            deleteBtn.style.bottom = "10px";
            deleteBtn.style.padding = "0 6px";
            deleteBtn.style.color = "#a00";
            deleteBtn.style.fontWeight = "bold";
            deleteBtn.style.background = "none";
            deleteBtn.style.border = "none";
            deleteBtn.style.cursor = "pointer";

            // When clicked, check the delete box and hide the form visually
            deleteBtn.onclick = () => {
                deleteCheckbox.checked = true;
                form.style.opacity = "0.4";
                form.style.pointerEvents = "none";
            };

            // Append it to the form
            form.appendChild(deleteBtn);
        }
    });
});
