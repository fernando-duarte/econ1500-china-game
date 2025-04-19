/**
 * China Growth Game - Game Dashboard
 * This is the main game interface, integrating with the game's backend
 */

import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Slider from "@mui/material/Slider";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";

// Socket.io for real-time communication
import io from "socket.io-client";

function GameDashboard() {
  // State for game data
  const [gameState, setGameState] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teams, setTeams] = useState([]);
  const [round, setRound] = useState(0);
  const [serverConnected, setServerConnected] = useState(false);
  const [modelConnected, setModelConnected] = useState(false);
  const [events, setEvents] = useState([]);
  
  // Game decision state
  const [savingsRate, setSavingsRate] = useState(0.2);
  const [exchangeRatePolicy, setExchangeRatePolicy] = useState("market");

  // Socket connection
  const [socket, setSocket] = useState(null);

  // Connect to the server when component mounts
  useEffect(() => {
    // Use explicit URL for Socket.IO connection
    const newSocket = io(process.env.REACT_APP_WS_URL || "http://localhost:4000", {
      transports: ['websocket', 'polling'],
      withCredentials: false
    });
    setSocket(newSocket);

    // Socket event listeners
    newSocket.on("connect", () => {
      console.log("Connected to server");
      setServerConnected(true);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from server");
      setServerConnected(false);
    });

    newSocket.on("gameState", (state) => {
      console.log("Game state updated:", state);
      setGameState(state);
      setTeams(state.teams || []);
      setRound(state.round || 0);
      setModelConnected(true);
    });

    newSocket.on("teamCreated", (team) => {
      console.log("Team created:", team);
      setTeams((prevTeams) => [...prevTeams, team]);
    });

    newSocket.on("roundAdvanced", (result) => {
      console.log("Round advanced:", result);
      setEvents((prevEvents) => [
        { 
          id: Date.now(), 
          type: "round", 
          message: `Round ${result.round} completed` 
        },
        ...prevEvents,
      ]);
    });

    newSocket.on("decisionSubmitted", (decision) => {
      console.log("Decision submitted:", decision);
      setEvents((prevEvents) => [
        { 
          id: Date.now(), 
          type: "decision", 
          message: `Team ${decision.team_name} submitted decision` 
        },
        ...prevEvents,
      ]);
    });

    newSocket.on("error", (error) => {
      console.error("Socket error:", error);
      setEvents((prevEvents) => [
        { 
          id: Date.now(), 
          type: "error", 
          message: error.message || "Unknown error" 
        },
        ...prevEvents,
      ]);
    });

    // Clean up the socket connection when component unmounts
    return () => {
      newSocket.disconnect();
    };
  }, []);

  // Functions for game actions
  const handleTeamSelect = (event) => {
    const teamId = event.target.value;
    const team = teams.find((t) => t.id === teamId);
    setSelectedTeam(team);
  };

  const handleCreateTeam = () => {
    const teamName = prompt("Enter a name for your team:");
    if (teamName && socket) {
      socket.emit("createTeam", teamName);
    }
  };

  const handleSubmitDecision = () => {
    if (selectedTeam && socket) {
      socket.emit("submitDecision", {
        teamId: selectedTeam.id,
        savingsRate,
        exchangeRatePolicy,
      });
    }
  };

  const handleStartGame = () => {
    if (socket) {
      socket.emit("startGame");
    }
  };

  const handleAdvanceRound = () => {
    if (socket) {
      socket.emit("advanceRound");
    }
  };

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>
        China's Growth Game
      </Typography>
      
      {/* Status Section */}
      <Grid container spacing={3} sx={{ marginBottom: 3 }}>
        <Grid item xs={12} md={6} lg={3}>
          <Box sx={{ marginBottom: 1.5 }}>
            <Typography variant="h6" fontWeight="medium">
              Server Status
            </Typography>
            {serverConnected ? (
              <Alert severity="success">Connected</Alert>
            ) : (
              <Alert severity="error">Disconnected</Alert>
            )}
          </Box>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Box sx={{ marginBottom: 1.5 }}>
            <Typography variant="h6" fontWeight="medium">
              Economic Model Status
            </Typography>
            {modelConnected ? (
              <Alert severity="success">Connected</Alert>
            ) : (
              <Alert severity="error">Disconnected</Alert>
            )}
          </Box>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Box sx={{ marginBottom: 1.5 }}>
            <Typography variant="h6" fontWeight="medium">
              Current Round
            </Typography>
            <Typography variant="h4">{round}</Typography>
          </Box>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Box sx={{ marginBottom: 1.5 }}>
            <Typography variant="h6" fontWeight="medium">
              Teams
            </Typography>
            <Typography variant="h4">{teams.length}</Typography>
          </Box>
        </Grid>
      </Grid>

      {/* Game Controls for Administrators */}
      <Grid container spacing={3} sx={{ marginBottom: 3 }}>
        <Grid item xs={12}>
          <Card>
            <Box sx={{ padding: 3 }}>
              <Typography variant="h6" fontWeight="medium" sx={{ marginBottom: 2 }}>
                Game Administration
              </Typography>
              <Grid container spacing={2}>
                <Grid item>
                  <Button variant="contained" color="primary" onClick={handleStartGame}>
                    Start Game
                  </Button>
                </Grid>
                <Grid item>
                  <Button variant="contained" color="warning" onClick={handleAdvanceRound}>
                    Advance Round
                  </Button>
                </Grid>
                <Grid item>
                  <Button variant="contained" color="info" onClick={handleCreateTeam}>
                    Create Team
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Card>
        </Grid>
      </Grid>

      {/* Team Selection and Decision Making */}
      <Grid container spacing={3} sx={{ marginBottom: 3 }}>
        <Grid item xs={12} lg={5}>
          <Card>
            <Box sx={{ padding: 3 }}>
              <Typography variant="h6" fontWeight="medium" sx={{ marginBottom: 2 }}>
                Team Selection
              </Typography>
              <FormControl fullWidth>
                <InputLabel id="team-select-label">Select Your Team</InputLabel>
                <Select
                  labelId="team-select-label"
                  id="team-select"
                  value={selectedTeam?.id || ""}
                  label="Select Your Team"
                  onChange={handleTeamSelect}
                >
                  {teams.map((team) => (
                    <MenuItem key={team.id} value={team.id}>
                      {team.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </Card>
        </Grid>
        <Grid item xs={12} lg={7}>
          <Card>
            <Box sx={{ padding: 3 }}>
              <Typography variant="h6" fontWeight="medium" sx={{ marginBottom: 2 }}>
                Decision Making
              </Typography>
              {selectedTeam ? (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ marginBottom: 2 }}>
                      <Typography variant="body2" sx={{ marginBottom: 1 }}>
                        Savings Rate: {(savingsRate * 100).toFixed(0)}%
                      </Typography>
                      <Slider
                        value={savingsRate}
                        onChange={(e, newValue) => setSavingsRate(newValue)}
                        min={0.01}
                        max={0.99}
                        step={0.01}
                        valueLabelDisplay="auto"
                        valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ marginBottom: 2 }}>
                      <Typography variant="body2" sx={{ marginBottom: 1 }}>
                        Exchange Rate Policy
                      </Typography>
                      <FormControl fullWidth>
                        <Select
                          value={exchangeRatePolicy}
                          onChange={(e) => setExchangeRatePolicy(e.target.value)}
                        >
                          <MenuItem value="market">Market Rate</MenuItem>
                          <MenuItem value="undervalue">Undervalue Currency</MenuItem>
                          <MenuItem value="overvalue">Overvalue Currency</MenuItem>
                        </Select>
                      </FormControl>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Button 
                      variant="contained" 
                      color="success" 
                      onClick={handleSubmitDecision}
                      fullWidth
                    >
                      Submit Decision
                    </Button>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  Please select a team to make decisions
                </Typography>
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>

      {/* Event Log */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <Box sx={{ padding: 3 }}>
              <Typography variant="h6" fontWeight="medium" sx={{ marginBottom: 2 }}>
                Event Log
              </Typography>
              <Box sx={{ maxHeight: '300px', overflow: 'auto' }}>
                {events.length > 0 ? (
                  events.map((event) => (
                    <Alert
                      key={event.id}
                      severity={event.type === 'error' ? 'error' : 'info'}
                      sx={{ marginBottom: 1 }}
                    >
                      {event.message}
                    </Alert>
                  ))
                ) : (
                  <Typography variant="body2" color="textSecondary">
                    No events to display
                  </Typography>
                )}
              </Box>
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default GameDashboard;
