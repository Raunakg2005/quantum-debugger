"use client";

import { useState, useEffect } from "react";
import EntranceScreen from "./components/EntranceScreen";

export default function Home() {
  const [particles, setParticles] = useState<Array<{ left: string; top: string }>>([]);

  useEffect(() => {
    setParticles(
      Array.from({ length: 30 }, () => ({
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
      }))
    );
  }, []);

  return <EntranceScreen particles={particles} />;
}
