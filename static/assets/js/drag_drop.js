document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    var containers = Array.prototype.slice.call(document.querySelectorAll('.draggable-list'));
    console.log('Containers found:', containers.length);

    if (containers.length === 0) {
        console.error('No containers found for dragula');
        return;
    }

    var drake = dragula(containers, {
        moves: function (el, container, handle) {
            console.log('Drag started for element:', el);
            return handle.classList.contains('draggable-item');
        }
    });
        drake.on('dragend', function(el) {
        console.log('Drag ended:', el);
    });


    drake.on('drop', function(el, target, source, sibling) {
        console.log('Element dropped:', el);

        // Check if the drop target is valid
        if (target) {
            const newStatus = target.closest('.kanban-column').querySelector('h3').textContent.toLowerCase().replace(/ /g, '_');
            const applicationId = el.getAttribute('data-id');

            console.log('New Status:', newStatus);
            console.log('Application ID:', applicationId);

            // Add your fetch call here for updating status
            fetch(`/update-application-status`, {
                method: 'POST',
                body: JSON.stringify({ id: applicationId, newStatus: newStatus}),
                headers: { 'Content-Type': 'application/json' },
            })
            .then(response => response.json())
            .then(data => {
                console.log('Status updated:', data);
                const updateElement = () => {
                window.location.reload(true); // Reload the entire page after all updates are completed
                };

                setTimeout(updateElement, 500); // Wait for 1 second before reloading

            })
            .catch(error => console.error('Error updating status:', error));




            // Fetch call to update application status on the server-side can go here
        } else {
            console.log('Dropped outside of valid targets. Returning item to source.');
            source.appendChild(el); // Move the item back to its original container
        }
    });

    // Optional: Handle dragging out of empty columns
    drake.on('over', function(el, container) {
            console.log('Over', el);

    });
    drake.on('cancel', function(el) {
        console.log('Drag canceled:', el);
    });


    drake.on('out', function(el, container) {
        console.log('Out of container:', container);
    });

});

