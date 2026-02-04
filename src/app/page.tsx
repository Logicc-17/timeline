"use client";
import { useEffect } from "react";

const Index = () => {
  useEffect(() => {
 
    window.location.href = "/malawi-news.html";
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <p className="text-muted-foreground">Redirecting to Malawi News Aggregator...</p>
      </div>
    </div>
  );
};

export default Index;
