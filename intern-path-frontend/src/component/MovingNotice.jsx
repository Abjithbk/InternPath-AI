import React from 'react';

const MovingNotice = () => {
  const message = "📢 Notice: Internship details are scraped from external platforms. For further details, click 'Apply' to visit the original site. We are here to provide opportunities for you!";

  return (
    <div className="marquee-container">
      <div className="animate-marquee">
        <span className="px-10 font-medium">{message}</span>
        <span className="px-10 font-medium">{message}</span>
      </div>
    </div>
  );
};

export default MovingNotice;