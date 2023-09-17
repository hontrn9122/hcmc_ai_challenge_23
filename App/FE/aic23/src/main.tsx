import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { SubmissionProvider } from "./context/Submission.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SubmissionProvider>
      <App />
    </SubmissionProvider>
  </React.StrictMode>
);
