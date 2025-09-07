// Football Focus API Usage Examples
// JavaScript/React integration examples

const API_BASE_URL = 'http://localhost:5000';

// Example 1: Fetch latest gameweek match reports
async function fetchLatestGameweek() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/gameweek/latest`);
    const data = await response.json();
    
    if (data.success) {
      console.log(`Matchday ${data.data.matchday}`);
      console.log(`${data.data.summary.total_matches} matches`);
      console.log(`${data.data.summary.total_goals} total goals`);
      
      data.data.match_reports.forEach(report => {
        console.log(`${report.home_team} ${report.home_score}-${report.away_score} ${report.away_team}`);
        console.log(`Report: ${report.title}`);
      });
      
      return data.data;
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Example 2: Fetch specific gameweek
async function fetchGameweek(matchday) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/gameweek/${matchday}`);
    const data = await response.json();
    
    if (data.success) {
      return data.data;
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Example 3: React Hook for gameweek data
function useGameweekData(matchday = 'latest') {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const endpoint = matchday === 'latest' 
          ? `${API_BASE_URL}/api/gameweek/latest`
          : `${API_BASE_URL}/api/gameweek/${matchday}`;
        
        const response = await fetch(endpoint);
        const result = await response.json();
        
        if (result.success) {
          setData(result.data);
          setError(null);
        } else {
          setError(result.error);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    
    fetchData();
  }, [matchday]);
  
  return { data, loading, error };
}

// Example 4: Match Report Card Component
function MatchReportCard({ report }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      {/* Match Header */}
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded">
          {report.competition}
        </span>
        <span className="text-sm text-gray-500">
          {new Date(report.match_date).toLocaleDateString()}
        </span>
      </div>
      
      {/* Teams and Score */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="font-medium">{report.home_team}</div>
          <div className="font-medium">{report.away_team}</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold">{report.score_display}</div>
          <span className={`text-xs px-2 py-1 rounded ${
            report.result === 'W' ? 'bg-green-100 text-green-700' :
            report.result === 'L' ? 'bg-red-100 text-red-700' :
            'bg-yellow-100 text-yellow-700'
          }`}>
            {report.result === 'W' ? 'HOME WIN' : 
             report.result === 'L' ? 'AWAY WIN' : 'DRAW'}
          </span>
        </div>
      </div>
      
      {/* Article */}
      <h3 className="font-bold mb-2">{report.title}</h3>
      <p className="text-gray-600 text-sm mb-3">{report.excerpt}</p>
      
      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-3">
        {report.tags.slice(0, 3).map((tag, index) => (
          <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
            {tag}
          </span>
        ))}
      </div>
      
      {/* Footer */}
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{report.author}</span>
        <span>{report.readTime}</span>
      </div>
    </div>
  );
}

// Example 5: Gameweek Summary Component
function GameweekSummary({ summary, matchday }) {
  return (
    <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-lg p-6 text-white mb-6">
      <h2 className="text-2xl font-bold mb-4">Matchday {matchday} Summary</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold">{summary.total_matches}</div>
          <div className="text-sm opacity-80">Matches</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold">{summary.total_goals}</div>
          <div className="text-sm opacity-80">Goals</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold">{summary.avg_goals_per_match}</div>
          <div className="text-sm opacity-80">Avg Goals</div>
        </div>
        
        <div className="text-center">
          <div className={`text-sm px-3 py-1 rounded-full ${
            summary.gameweek_complete ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
          }`}>
            {summary.gameweek_complete ? 'Complete' : 'In Progress'}
          </div>
        </div>
      </div>
    </div>
  );
}

// Example API Response Format:
/*
{
  "success": true,
  "data": {
    "matchday": 1,
    "match_reports": [
      {
        "id": 1,
        "title": "Manchester United 2-1 Arsenal: Late Drama at Old Trafford",
        "excerpt": "Bruno Fernandes scored a dramatic penalty...",
        "home_team": "Manchester United",
        "away_team": "Arsenal", 
        "home_score": 2,
        "away_score": 1,
        "score_display": "2-1",
        "result": "W",
        "match_date": "2025-08-15",
        "competition": "Premier League",
        "tags": ["Manchester United", "Arsenal", "Matchday 1"],
        "author": "Football Focus AI",
        "readTime": "5 min read"
      }
    ],
    "summary": {
      "total_matches": 10,
      "total_goals": 28,
      "avg_goals_per_match": 2.8,
      "gameweek_complete": true
    }
  }
}
*/

export {
  fetchLatestGameweek,
  fetchGameweek,
  useGameweekData,
  MatchReportCard,
  GameweekSummary
};
