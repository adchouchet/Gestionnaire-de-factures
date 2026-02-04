// Gestion du thème (Enforced Dark Mode)
document.addEventListener('DOMContentLoaded', function () {
    // Theme is enforced in base.html head. No JS toggling needed.
});

// Calcul dynamique du total de la facture
function updateInvoiceTotal() {
    const formset = document.getElementById('invoice-formset');
    if (!formset) return;

    let total = 0;
    const rows = formset.querySelectorAll('.formset-row');

    rows.forEach(row => {
        const productSelect = row.querySelector('select[name$="-product"]');
        const quantityInput = row.querySelector('input[name$="-quantity"]');
        const deleteCheckbox = row.querySelector('input[name$="-DELETE"]');

        if (productSelect && quantityInput && !deleteCheckbox?.checked) {
            const selectedOption = productSelect.options[productSelect.selectedIndex];
            if (selectedOption && selectedOption.value) {
                const price = parseFloat(selectedOption.dataset.price || 0);
                const quantity = parseInt(quantityInput.value || 0);
                total += price * quantity;
            }
        }
    });

    const totalDisplay = document.getElementById('total-display');
    if (totalDisplay) {
        totalDisplay.textContent = total.toFixed(2) + ' €';
    }
}

// Écouter les changements dans le formset
document.addEventListener('DOMContentLoaded', function () {
    const formset = document.getElementById('invoice-formset');
    if (formset) {
        formset.addEventListener('change', updateInvoiceTotal);
        formset.addEventListener('input', updateInvoiceTotal);
        updateInvoiceTotal(); // Calcul initial
    }
});

// Confirmation de suppression
function confirmDelete(event, itemName) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer "${itemName}" ?`)) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Auto-dismiss des messages après 5 secondes
document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Animation de sortie pour les messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
