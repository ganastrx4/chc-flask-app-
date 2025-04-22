import React from "react";
import { IDKitWidget } from "@worldcoin/idkit";
import { useToast } from "@/components/ui/use-toast";

const WorldIDVerification = () => {
  const { toast } = useToast();

  const onSuccess = (result) => {
    toast({
      title: "Verification Successful",
      description: "Your identity has been verified with World ID",
    });
    console.log("Verification successful:", result);
  };

  const handleVerify = async (proof) => {
    try {
      console.log("Proof received:", proof);
      return true;
    } catch (error) {
      console.error("Verification error:", error);
      toast({
        title: "Verification Error",
        description: "There was an error verifying your identity",
        variant: "destructive",
      });
      return false;
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-background to-secondary/20">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">World ID Verification</h1>
        <p className="text-muted-foreground">
          Verify your identity using World ID
        </p>
      </div>
      
      <div className="p-8 rounded-lg bg-card border shadow-lg">
        <IDKitWidget
          app_id="app_7686f9027d3e3c0b53d987a3caf1e111" // Reemplaza con tu app ID real
          action="verify"
          onSuccess={onSuccess}
          handleVerify={handleVerify}
          verification_level="orb"
        >
          {({ open }) => (
            <button
              onClick={open}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
            >
              Verify with World ID
            </button>
          )}
        </IDKitWidget>
      </div>
    </div>
  );
};

export default WorldIDVerification;
