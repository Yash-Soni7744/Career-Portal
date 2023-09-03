// Check if the browser supports service workers
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.register('/static/service-worker/push-notification.js') // Register the service worker
        .then(function(registration) {
            console.log('Service Worker registered with scope:', registration.scope);
        })
        .catch(function(error) {
            console.error('Service Worker registration failed:', error);
        });
}

document.getElementById('subscribe').addEventListener('click', subscribeUser);

// Function to subscribe the user to push notifications
function subscribeUser() {
    navigator.serviceWorker.ready.then(function(registration) {
        return registration.pushManager.subscribe({ userVisibleOnly: true });
    }).then(function(subscription) {
        // Send the subscription data to your server
        sendSubscriptionToServer(subscription);
        console.log('User is subscribed:', subscription);
    }).catch(function(error) {
        console.error('Subscription failed:', error);
    });
}

// Function to send the subscription data to your server
function sendSubscriptionToServer(subscription) {
    // Send a POST request to your Flask server to store the subscription
    fetch('/api/push-notification/subscribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subscription }),
    }).then(function(response) {
        if (!response.ok) {
            console.error('Failed to store subscription on the server.');
        }
    }).catch(function(error) {
        console.error('Error sending subscription to server:', error);
    });
}
