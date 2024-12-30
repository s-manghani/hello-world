import React, { useState, useCallback, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DoorOpen, Trophy, Gift } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const MontyHallGame = () => {
  const [gameState, setGameState] = useState('initial');
  const [doors, setDoors] = useState([
    { id: 0, content: null, isOpen: false },
    { id: 1, content: null, isOpen: false },
    { id: 2, content: null, isOpen: false },
  ]);
  const [carPosition, setCarPosition] = useState(null);
  const [playerChoice, setPlayerChoice] = useState(null);
  const [revealedDoor, setRevealedDoor] = useState(null);
  const [gameResult, setGameResult] = useState(null);
  const [simulationResults, setSimulationResults] = useState(null);
  const [currentBatchSize, setCurrentBatchSize] = useState(null);
  const [simulationMessage, setSimulationMessage] = useState('');
  
  // Initialize game
  const initializeGame = useCallback(() => {
    const newCarPosition = Math.floor(Math.random() * 3);
    const newDoors = [0, 1, 2].map(index => ({
      id: index,
      content: index === newCarPosition ? 'car' : 'goat',
      isOpen: false
    }));
    
    setDoors(newDoors);
    setCarPosition(newCarPosition);
    setPlayerChoice(null);
    setRevealedDoor(null);
    setGameResult(null);
    setSimulationResults(null);
    setCurrentBatchSize(null);
    setSimulationMessage('');
    setGameState('initial');
  }, []);

  const handleDoorPick = (doorId) => {
    if (gameState !== 'initial') return;
    setPlayerChoice(doorId);
    
    const possibleReveals = doors
      .filter(door => door.id !== doorId && door.content === 'goat')
      .map(door => door.id);
    const revealId = possibleReveals[Math.floor(Math.random() * possibleReveals.length)];
    
    setRevealedDoor(revealId);
    setDoors(doors.map(door => 
      door.id === revealId ? { ...door, isOpen: true } : door
    ));
    setGameState('doorPicked');
  };

  const handleDecision = (shouldSwitch) => {
    if (gameState !== 'doorPicked') return;
    
    let finalChoice = playerChoice;
    if (shouldSwitch) {
      finalChoice = doors.findIndex((door, index) => 
        index !== playerChoice && index !== revealedDoor
      );
      setPlayerChoice(finalChoice);
    }
    
    setDoors(doors.map(door => ({ ...door, isOpen: true })));
    setGameResult(finalChoice === carPosition);
    setGameState('final');
  };

  const runBatchSimulation = async (batchSize) => {
    let stayWins = 0;
    let switchWins = 0;
    
    for (let i = 0; i < batchSize; i++) {
      const simCarPos = Math.floor(Math.random() * 3);
      const simPlayerChoice = Math.floor(Math.random() * 3);
      
      const possibleReveals = [0, 1, 2].filter(
        door => door !== simPlayerChoice && door !== simCarPos
      );
      
      if (simPlayerChoice === simCarPos) stayWins++;
      
      const remainingDoor = [0, 1, 2].find(
        door => door !== simPlayerChoice && !possibleReveals.includes(door)
      );
      if (remainingDoor === simCarPos) switchWins++;
    }
    
    return {
      stayWinRate: (stayWins / batchSize) * 100,
      switchWinRate: (switchWins / batchSize) * 100,
      games: batchSize
    };
  };

  const runSimulation = async () => {
    if (gameState !== 'final') return;
    
    const batchSizes = [5, 10, 100, 1000, 3000, 5000, 10000, 50000, 1000000];
    const results = [];
    
    for (const batchSize of batchSizes) {
      setCurrentBatchSize(batchSize);
      setSimulationMessage(`Running simulation for ${batchSize} games...`);
      
      // Add a small delay for visual feedback
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const batchResults = await runBatchSimulation(batchSize);
      results.push(batchResults);
      setSimulationResults([...results]);
    }
    
    setSimulationMessage('All simulations complete!');
    setGameState('simulation');
  };

  return (
    <Card className="w-full max-w-4xl mx-auto p-6">
      <CardContent className="space-y-6">
        {/* Game Status */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold mb-2">Monty Hall Game</h2>
          <p className="text-gray-600">
            {gameState === 'initializing' && (
              <p className="text-gray-600">Loading game...</p>
            )}
            {gameState === 'initial' && "Pick a door!"}
            {gameState === 'doorPicked' && "Would you like to stick with your choice or switch?"}
            {gameState === 'final' && `You ${gameResult ? 'won' : 'lost'}! The car was behind door ${carPosition + 1}`}
            {gameState === 'simulation' && "Simulation complete!"}
          </p>
        </div>

        {/* Doors */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {doors.map((door, index) => (
            <div 
              key={door.id} 
              className={`relative cursor-pointer transition-transform ${
                playerChoice === index ? 'ring-2 ring-blue-500' : ''
              } ${door.isOpen ? 'opacity-75' : 'hover:scale-105'}`}
              onClick={() => handleDoorPick(index)}
            >
              <div className="bg-slate-200 p-8 rounded-lg text-center min-h-[200px] flex flex-col items-center justify-center">
                {door.isOpen ? (
                  <>
                    {door.content === 'car' ? (
                      <Trophy size={64} className="text-blue-500 mb-2" />
                    ) : (
                      <Gift size={64} className="text-gray-500 mb-2" />
                    )}
                    <div className="text-sm">{door.content === 'car' ? 'Car!' : 'Goat'}</div>
                  </>
                ) : (
                  <>
                    <DoorOpen size={64} className="text-yellow-700 mb-2" />
                    <div className="text-sm">Click to choose</div>
                  </>
                )}
              </div>
              <div className="text-center mt-2">Door {index + 1}</div>
            </div>
          ))}
        </div>

        {/* Game Controls */}
        <div className="flex justify-center gap-4">
          {gameState === 'doorPicked' && (
            <>
              <Button onClick={() => handleDecision(false)}>
                Stick
              </Button>
              <Button onClick={() => handleDecision(true)}>
                Switch
              </Button>
            </>
          )}
          {gameState === 'final' && (
            <Button onClick={runSimulation}>
              Run Simulation
            </Button>
          )}
          {(gameState === 'final' || gameState === 'simulation') && (
            <Button onClick={initializeGame}>
              Play Again
            </Button>
          )}
        </div>

        {/* Simulation Status */}
        {simulationMessage && (
          <div className="text-center text-blue-600 font-semibold">
            {simulationMessage}
          </div>
        )}

        {/* Simulation Results */}
        {simulationResults && (
          <div className="mt-8 p-4 bg-gray-100 rounded-lg">
            <h3 className="text-xl font-bold mb-4">Simulation Results</h3>
            <p className="text-sm text-gray-600 mb-4">
              Observe the convergence pattern:
              • With very few games (5-10), results can vary widely
              • Around 100 games, we start seeing more stable patterns
              • By 1000 games, we're typically within ±2% of theoretical values
              • At 10000 games, we're usually within ±1% of theoretical probabilities
              • At 50000 games, we see very close convergence
              • At 1 million games, we get extremely precise convergence to 33.33% (stay) and 66.67% (switch)
            </p>
            
            {/* Results Chart */}
            <div className="h-96 mb-8">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={simulationResults}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="games" 
                    label={{ 
                      value: 'Number of Games', 
                      position: 'insideBottom',
                      offset: -5,
                      style: {
                        fontSize: '1.2em',
                        fill: '#666',
                        fontWeight: 500
                      }
                    }}
                    tick={{fontSize: 12}}
                  />
                  <YAxis 
                    label={{ 
                      value: 'Win Rate (%)', 
                      angle: -90, 
                      position: 'insideLeft',
                      offset: 15,
                      style: {
                        fontSize: '1.2em',
                        fill: '#666',
                        fontWeight: 500
                      }
                    }}
                    domain={[0, 100]}
                    tick={{fontSize: 12}}
                  />
                  <Tooltip />
                  <Legend />
                  {/* Reference lines for theoretical probabilities */}
                  <ReferenceLine y={66.67} stroke="#82ca9d" strokeDasharray="3 3" label={{ 
                    value: 'Theoretical Switch (66.67%)',
                    position: 'right',
                    fill: '#82ca9d'
                  }} />
                  <ReferenceLine y={33.33} stroke="#8884d8" strokeDasharray="3 3" label={{ 
                    value: 'Theoretical Stay (33.33%)',
                    position: 'right',
                    fill: '#8884d8'
                  }} />
                  <Line 
                    type="monotone" 
                    dataKey="switchWinRate" 
                    name="Switch Strategy" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="stayWinRate" 
                    name="Stay Strategy" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Detailed Results */}
            <div className="space-y-6">
              {simulationResults.map((result) => (
                <div key={result.games} className="border-b pb-4">
                  <h4 className="font-semibold mb-2">After {result.games} games:</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-gray-600">Stay strategy:</p>
                      <p className="text-lg">{result.stayWinRate.toFixed(1)}% win rate</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Switch strategy:</p>
                      <p className="text-lg">{result.switchWinRate.toFixed(1)}% win rate</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <p className="text-sm text-gray-600 mt-4">
              Theoretical probabilities: Stay (33.33%), Switch (66.67%)
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MontyHallGame;
