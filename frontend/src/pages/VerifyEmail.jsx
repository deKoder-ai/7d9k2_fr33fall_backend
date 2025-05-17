// frontend/src/pages/VerifyEmail.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

export default function VerifyEmail() {
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState(false);
  const { token } = useParams();

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        await axios.post(`/api/verify-email/${token}/`);
        setVerified(true);
      } catch (err) {
        setError(true);
      }
    };

    verifyEmail();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        {verified ? (
          <>
            <div className="rounded-md bg-green-50 p-4">
              <div className="text-sm text-green-700">
                Email successfully verified! You can now log in.
              </div>
            </div>
            <a
              href="/"
              className="inline-block mt-4 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Go to login
            </a>
          </>
        ) : (
          error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">
                Invalid or expired verification token.
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
