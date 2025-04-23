import React from "react";
import { IDKitWidget, VerificationLevel } from "@worldcoin/idkit";

const verifyProof = async (proof) => {
  try {
    const res = await fetch("https://88f0-189-217-209-99.ngrok-free.app/api/verify-proof", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(proof),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error?.error || "Error al verificar con el backend.");
    }

    const data = await res.json();
    if (!data.success) {
      throw new Error("La verificación falló.");
    }

    console.log("✅ Verificación exitosa con el servidor");
    return true;
  } catch (err) {
    console.error("❌ Error en verificación:", err.message);
    throw err;
  }
};

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center text-gray-800">
          Verificar identidad con World ID
        </h1>
        <p className="text-center text-gray-600">
          Verifica tu identidad de forma segura y privada
        </p>

        <div className="flex justify-center">
          <IDKitWidget
            app_id="app_7686f9027d3e3c0b53d987a3caf1e111"
            action="ingreso"
            verification_level={VerificationLevel.Device}
            handleVerify={verifyProof}
            onSuccess={() => {
              console.log("✅ Usuario autenticado");
              window.location.href = "https://ganastrx4.github.io/chc-flask-app-/buscador.html";
            }}
          >
            {({ open }) => (
              <button
                onClick={open}
                className="inline-flex items-center justify-center text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-2 px-6 rounded-lg transform transition hover:scale-105"
              >
                Verificar con World ID
              </button>
            )}
          </IDKitWidget>
        </div>

        <div className="text-center text-sm text-gray-500">
          Al verificar, aceptas los términos y condiciones de World ID
        </div>
      </div>
    </div>
  );
}

export default App;
