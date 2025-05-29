import React from 'react';
import GaugeChart from 'react-gauge-chart';

const Speedometer = ({ speed }) => {
  const maxSpeed = 240;

  const currentSpeed = (typeof speed === 'number' && !isNaN(speed)) ? speed : 0;
  const percent = currentSpeed / maxSpeed;

  const chartStyle = {
    height: 200,
    width: 300,
  };

  return (
    <div className="speedometer-container">
      <h3>Velocidade</h3>
      <GaugeChart
        id="speedometer-gauge"
        style={chartStyle}
        nrOfLevels={24}
        arcsLength={[0.4, 0.2, 0.4]} 
        colors={['#5BE12C', '#F5CD19', '#EA4228']}
        percent={percent > 1 ? 1 : (percent < 0 ? 0 : percent)}
        arcPadding={0.02}
        cornerRadius={3}
        textColor="#FFFFFF"
        needleColor="#E0E0E0"
        needleBaseColor="#C0C0C0"
        formatTextValue={value => `${currentSpeed.toFixed(0)} km/h`}
      />
    </div>
  );
};

export default Speedometer;