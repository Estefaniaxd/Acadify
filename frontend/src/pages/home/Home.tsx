import React, { useState, useEffect } from 'react';
import HeroSection from '../../components/layout/HeroSection';
import VideoSection from '../../components/layout/VideoSection';
import Preloader from '../../components/layout/Preloader';
import FeaturesSection from '../../components/layout/FeaturesSection';
import HowItWorksSection from '../../components/layout/HowItWorksSection';
import OpenSourceSection from '../../components/layout/OpenSourceSection';
import TestimonialsSection from '../../components/layout/TestimonialsSection';
import InstitutionRegisterSection from '../../components/layout/InstitutionRegisterSection';
import RoadmapSection from '../../components/layout/RoadmapSection';
import FinalCTASection from '../../components/layout/FinalCTASection';


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
          <div id="inicio">
            <HeroSection />
          </div>
          <div id="video">
            <VideoSection />
          </div>
          <div id="caracteristicas">
            <FeaturesSection />
          </div>
          <div id="como-funciona">
            <HowItWorksSection />
          </div>
          <div id="open-source">
            <OpenSourceSection />
          </div>
          <div id="testimonios">
            <TestimonialsSection />
          </div>
          <div id="registro-instituciones">
            <InstitutionRegisterSection />
          </div>
          <div id="roadmap">
            <RoadmapSection />
          </div>
          <div id="unete">
            <FinalCTASection />
          </div>
        </>
      )}
    </>
  );
}
