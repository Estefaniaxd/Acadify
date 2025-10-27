import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import HeroSection from '../components/layout/HeroSection';
import VideoSection from '../components/layout/VideoSection';
import Preloader from '../components/layout/Preloader';
import FeaturesSection from '../components/layout/FeaturesSection';
import HowItWorksSection from '../components/layout/HowItWorksSection';
import OpenSourceSection from '../components/layout/OpenSourceSection';
import TestimonialsSection from '../components/layout/TestimonialsSection';
import InstitutionRegisterSection from '../components/layout/InstitutionRegisterSection';
import RoadmapSection from '../components/layout/RoadmapSection';
import FinalCTASection from '../components/layout/FinalCTASection';


export default function Home() {
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <Preloader show={loading} />
      {!loading && (
        <>
          <HeroSection />
          <VideoSection />
          <FeaturesSection />
          <HowItWorksSection />
          <OpenSourceSection />
          <TestimonialsSection />
          <InstitutionRegisterSection />
          <RoadmapSection />
          <FinalCTASection />
        </>
      )}
    </>
  );
}
