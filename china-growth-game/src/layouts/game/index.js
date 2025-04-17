/**
 * China Growth Game - Game Dashboard
 * This is the main game interface, integrating Material Dashboard with the game's backend
 */

import { useState, useEffect } from "react";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Slider from "@mui/material/Slider";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDAlert from "components/MDAlert";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Data visualization components
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";

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
  const [exchangeRatePolicy, setExchangeRatePolicy] = useState("fixed");

  // Socket connection
  const [socket, setSocket] = useState(null);

  // Connect to the server when component mounts
  useEffect(() => {
    // Use explicit URL for Socket.IO connection to avoid port confusion
    const newSocket = io("http://localhost:3000", {
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
      // Update events with the round results
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
      // Update events with the decision
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
      // Add error to events
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

  // Prepare chart data
  const gdpChartData = {
    labels: Array.from({ length: round + 1 }, (_, i) => `Round ${i}`),
    datasets: {
      label: "GDP",
      data: gameState?.rounds?.map(r => r.gdp) || [],
    },
  };

  const consumptionChartData = {
    labels: Array.from({ length: round + 1 }, (_, i) => `Round ${i}`),
    datasets: {
      label: "Consumption",
      data: gameState?.rounds?.map(r => r.consumption) || [],
    },
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* Status Section */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <MDTypography variant="h6" fontWeight="medium">
                Server Status
              </MDTypography>
              {serverConnected ? (
                <MDAlert color="success">Connected</MDAlert>
              ) : (
                <MDAlert color="error">Disconnected</MDAlert>
              )}
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <MDTypography variant="h6" fontWeight="medium">
                Economic Model Status
              </MDTypography>
              {modelConnected ? (
                <MDAlert color="success">Connected</MDAlert>
              ) : (
                <MDAlert color="error">Disconnected</MDAlert>
              )}
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <MDTypography variant="h6" fontWeight="medium">
                Current Round
              </MDTypography>
              <MDTypography variant="h4">{round}</MDTypography>
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <MDTypography variant="h6" fontWeight="medium">
                Teams
              </MDTypography>
              <MDTypography variant="h4">{teams.length}</MDTypography>
            </MDBox>
          </Grid>
        </Grid>

        {/* Game Controls for Administrators */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" fontWeight="medium" mb={2}>
                  Game Administration
                </MDTypography>
                <Grid container spacing={2}>
                  <Grid item>
                    <MDButton variant="contained" color="info" onClick={handleStartGame}>
                      Start Game
                    </MDButton>
                  </Grid>
                  <Grid item>
                    <MDButton variant="contained" color="warning" onClick={handleAdvanceRound}>
                      Advance Round
                    </MDButton>
                  </Grid>
                  <Grid item>
                    <MDButton variant="contained" color="primary" onClick={handleCreateTeam}>
                      Create Team
                    </MDButton>
                  </Grid>
                </Grid>
              </MDBox>
            </Card>
          </Grid>
        </Grid>

        {/* Team Selection and Decision Making */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} lg={5}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" fontWeight="medium" mb={2}>
                  Team Selection
                </MDTypography>
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
              </MDBox>
            </Card>
          </Grid>
          <Grid item xs={12} lg={7}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" fontWeight="medium" mb={2}>
                  Decision Making
                </MDTypography>
                {selectedTeam ? (
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <MDBox mb={2}>
                        <MDTypography variant="body2" fontWeight="regular" mb={1}>
                          Savings Rate: {(savingsRate * 100).toFixed(0)}%
                        </MDTypography>
                        <Slider
                          value={savingsRate}
                          onChange={(e, newValue) => setSavingsRate(newValue)}
                          min={0}
                          max={0.5}
                          step={0.01}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                        />
                      </MDBox>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <MDBox mb={2}>
                        <MDTypography variant="body2" fontWeight="regular" mb={1}>
                          Exchange Rate Policy
                        </MDTypography>
                        <FormControl fullWidth>
                          <Select
                            value={exchangeRatePolicy}
                            onChange={(e) => setExchangeRatePolicy(e.target.value)}
                          >
                            <MenuItem value="fixed">Fixed Exchange Rate</MenuItem>
                            <MenuItem value="floating">Floating Exchange Rate</MenuItem>
                          </Select>
                        </FormControl>
                      </MDBox>
                    </Grid>
                    <Grid item xs={12}>
                      <MDButton 
                        variant="contained" 
                        color="success" 
                        onClick={handleSubmitDecision}
                        fullWidth
                      >
                        Submit Decision
                      </MDButton>
                    </Grid>
                  </Grid>
                ) : (
                  <MDTypography variant="body2" color="text">
                    Please select a team to make decisions
                  </MDTypography>
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>

        {/* Charts & Data Visualization */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} lg={6}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" fontWeight="medium" mb={1}>
                  GDP Growth Over Time
                </MDTypography>
                <ReportsLineChart
                  color="success"
                  title="GDP"
                  description="Economic growth over time"
                  date="updated every round"
                  chart={gdpChartData}
                />
              </MDBox>
            </Card>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" fontWeight="medium" mb={1}>
                  Consumption Over Time
                </MDTypography>
                <ReportsBarChart
                  color="info"
                  title="Consumption"
                  description="Consumption levels over time"
                  date="updated every round"
                  chart={consumptionChartData}
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>

        {/* Event Log */}
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" fontWeight="medium" mb={2}>
                  Event Log
                </MDTypography>
                <MDBox sx={{ maxHeight: '300px', overflow: 'auto' }}>
                  {events.length > 0 ? (
                    events.map((event) => (
                      <MDAlert
                        key={event.id}
                        color={event.type === 'error' ? 'error' : 'info'}
                        dismissible
                        mb={1}
                      >
                        {event.message}
                      </MDAlert>
                    ))
                  ) : (
                    <MDTypography variant="body2" color="text">
                      No events to display
                    </MDTypography>
                  )}
                </MDBox>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default GameDashboard; 