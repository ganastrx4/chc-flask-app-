import React from "react";
import { Toaster } from "@/components/ui/toaster";
import WorldIDVerification from "@/components/WorldIDVerification";

function App() {
  return (
    <>
      <WorldIDVerification />
      <Toaster />
    </>
  );
}

export default App;
