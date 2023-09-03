"use strict";

if (typeof localStorage !== "undefined") {
  console.log("localStorage is available");
  if (localStorage.getItem("notification-identifier") === null)
    localStorage.setItem("notification-identifier", uuidv4());  
} else {
  console.log("localStorage is not available");
}

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
  .replace(/[xy]/g, function (c) {
      const r = Math.random() * 16 | 0, 
          v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
  });
}

const applicationServerPublicKey =
  "BI20wiA0b0BfvDimVNxstFYT7eyRh9x54mvfEvS54yZgPHxJQkQ3B3G-QDhmEhpcliKseZ02I3quhM2_Q9ZIXYQ";

const pushButton = document.getElementById("subscribeBtn");

let isSubscribed = false;
let swRegistration = null;

function urlB64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, "+")
    .replace(/_/g, "/");

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function updateSubscriptionOnServer(subscription) {
  fetch("/api/push-notification/subscribe", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "subscription": subscription,
      "notification-identifier": localStorage.getItem("notification-identifier"),
    }),
    
  })
    .then(function (response) {
      if (response.ok) {
        console.log("Subscription updated on server");
      }
    })
    .catch(function (error) {
      console.log("Error sending subscription to server: ", error);
    });
}

function subscribeUser() {
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  swRegistration.pushManager
    .subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey,
    })
    .then(function (subscription) {
      console.log("User is subscribed, sending subscription to server");

      console.log("User is now subscribed.");

      updateSubscriptionOnServer(subscription);

      isSubscribed = true;
      pushButton.style.display = "none";
    })
    .catch(function (err) {
      pushButton.textContent = "Permission denied";
      console.log("Failed to subscribe the user: ", err);
    });
}

function initializeUI() {
  pushButton.addEventListener("click", function () {
    pushButton.disabled = true;
    if (isSubscribed) {
      console.log("User is already subscribed");
    } else {
      console.log("User is not subscribed, subsribing user");
      subscribeUser();
    }
  });

  // Set the initial subscription value
  swRegistration.pushManager.getSubscription().then(function (subscription) {
    isSubscribed = !(subscription === null);

    updateSubscriptionOnServer(subscription);

    if (isSubscribed) {
      pushButton.style.display = "none";
      console.log("User is already subscribed.");
    } else {
      pushButton.style.display = "block";
      console.log("User is not subscribed.");
    }
  });
}

if ("serviceWorker" in navigator && "PushManager" in window) {
  console.log("Service Worker and Push is supported");

  navigator.serviceWorker
    .register("/static/service-worker/push-notification.js")
    .then(function (swReg) {
      console.log("Service Worker is registered");

      swRegistration = swReg;
      initializeUI();
    })
    .catch(function (error) {
      console.error("Service Worker Error", error);
    });
} else {
  console.warn("Push messaging is not supported");
  pushButton.textContent = "Push Not Supported";
}
