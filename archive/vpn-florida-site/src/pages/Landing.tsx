import Hero from "../sections/Hero";
import Devices from "../sections/Devices";
import WhyUs from "../sections/WhyUs";
import Payment from "../sections/Payment";
import Footer from "../sections/Footer";

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Hero />
      <Devices />
      <WhyUs />
      <Payment />
      <Footer />
    </div>
  );
}
