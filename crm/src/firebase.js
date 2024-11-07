// src/firebase.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCrSEhQdK0VHYit7ZkTW8JevF9is0CbRqc",
  authDomain: "wayne-carpet.firebaseapp.com",
  projectId: "wayne-carpet",
  storageBucket: "wayne-carpet.appspot.com",
  messagingSenderId: "570695445734",
  appId: "1:570695445734:web:d5fb7d0a32a6260403df27"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
const firestore = getFirestore(app);

export { app, firestore };
