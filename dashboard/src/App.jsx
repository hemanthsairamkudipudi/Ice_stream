import { useCallback, useEffect, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react'

import '@xyflow/react/dist/style.css'
import './App.css'

const initialNodes = [
  {
    id: 'generator',
    position: { x: 50, y: 100 },
    data: {
      label: 'Checkout Generator\nLIVE',
    },
    style: {
      background: '#ffffff',
      border: '2px solid #16a34a',
      borderRadius: '10px',
      padding: '15px',
      width: 190,
      fontWeight: '600',
      whiteSpace: 'pre-line',
      textAlign: 'center',
    },
  },
  {
    id: 'kafka',
    position: { x: 300, y: 100 },
    data: {
      label: 'Kafka\nLIVE',
    },
    style: {
      background: '#ffffff',
      border: '2px solid #16a34a',
      borderRadius: '10px',
      padding: '15px',
      width: 190,
      fontWeight: '600',
      whiteSpace: 'pre-line',
      textAlign: 'center',
    },
  },
  {
    id: 'flink',
    position: { x: 550, y: 100 },
    data: {
      label: 'Flink\nLIVE',
    },
    style: {
      background: '#ffffff',
      border: '2px solid #16a34a',
      borderRadius: '10px',
      padding: '15px',
      width: 190,
      fontWeight: '600',
      whiteSpace: 'pre-line',
      textAlign: 'center',
    },
  },
  {
    id: 'iceberg',
    position: { x: 800, y: 100 },
    data: {
      label: 'Iceberg\nLIVE',
    },
    style: {
      background: '#ffffff',
      border: '2px solid #16a34a',
      borderRadius: '10px',
      padding: '15px',
      width: 190,
      fontWeight: '600',
      whiteSpace: 'pre-line',
      textAlign: 'center',
    },
  },
  {
    id: 'quality',
    position: { x: 1050, y: 100 },
    data: {
      label: 'Data Quality\nPLANNED',
    },
    style: {
      background: '#ffffff',
      border: '2px solid #f59e0b',
      borderRadius: '10px',
      padding: '15px',
      width: 190,
      fontWeight: '600',
      whiteSpace: 'pre-line',
      textAlign: 'center',
    },
  },
  {
    id: 'observability',
    position: { x: 1300, y: 100 },
    data: {
      label: 'Observability\nPLANNED',
    },
    style: {
      background: '#ffffff',
      border: '2px solid #f59e0b',
      borderRadius: '10px',
      padding: '15px',
      width: 190,
      fontWeight: '600',
      whiteSpace: 'pre-line',
      textAlign: 'center',
    },
  },
]

const initialEdges = [
  {
    id: 'generator-kafka',
    source: 'generator',
    target: 'kafka',
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: 'kafka-flink',
    source: 'kafka',
    target: 'flink',
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: 'flink-iceberg',
    source: 'flink',
    target: 'iceberg',
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: 'iceberg-quality',
    source: 'iceberg',
    target: 'quality',
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: 'quality-observability',
    source: 'quality',
    target: 'observability',
    markerEnd: { type: MarkerType.ArrowClosed },
  },
]

function StatusCard({ title, value, status }) {
  return (
    <div className="summary-card">
      <div className="summary-title">{title}</div>
      <div className="summary-value">{value}</div>

      {status && (
        <div className={`summary-status ${status.toLowerCase()}`}>
          <span className="summary-status-dot"></span>
          {status}
        </div>
      )}
    </div>
  )
}

function IncidentCard({ incident }) {
  if (!incident) {
    return (
      <div className="incident-card healthy">
        <div className="incident-header">
          <h3>Incident Log</h3>
          <span className="incident-badge closed">NO ACTIVE INCIDENT</span>
        </div>

        <p className="incident-empty">
          The remediation pipeline is currently healthy.
        </p>
      </div>
    )
  }

  return (
    <div className="incident-card">
      <div className="incident-header">
        <h3>Incident Log</h3>

        <span
          className={`incident-badge ${incident.state.toLowerCase()}`}
        >
          {incident.state}
        </span>
      </div>

      <div className="incident-grid">
        <div>
          <span className="incident-label">Incident ID</span>
          <strong>{incident.incident_id}</strong>
        </div>

        <div>
          <span className="incident-label">Detected</span>
          <strong>
            {new Date(incident.detected_at).toLocaleString()}
          </strong>
        </div>

        <div>
          <span className="incident-label">Failed Records</span>
          <strong>
            {incident.failed_records} / {incident.total_records}
          </strong>
        </div>

        <div>
          <span className="incident-label">Error Rate</span>
          <strong>
            {(incident.error_rate * 100).toFixed(1)}%
          </strong>
        </div>

        <div>
          <span className="incident-label">Threshold</span>
          <strong>
            {(incident.threshold * 100).toFixed(1)}%
          </strong>
        </div>

        <div>
          <span className="incident-label">Quarantined</span>
          <strong>{incident.quarantined_records}</strong>
        </div>
      </div>

      <div className="incident-action">
        <span className="incident-label">Action</span>
        <strong>{incident.action}</strong>
      </div>

      {incident.failure_reasons?.length > 0 && (
        <div className="incident-reasons">
          <span className="incident-label">Failure Reasons</span>

          <ul>
            {incident.failure_reasons.map((reason, index) => (
              <li key={`${reason}-${index}`}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function IncidentHistory({ incidents }) {
  return (
    <div className="incident-history">
      <div className="incident-header">
        <h3>Incident History</h3>
        <span className="incident-count">
          {incidents.length} recorded
        </span>
      </div>

      {incidents.length === 0 ? (
        <p className="incident-empty">
          No incidents have been recorded.
        </p>
      ) : (
        <div className="incident-history-list">
          {incidents.map((incident) => (
            <div
              className="incident-history-item"
              key={incident.incident_id}
            >
              <div>
                <strong>{incident.incident_id}</strong>
                <span>
                  {new Date(incident.detected_at).toLocaleString()}
                </span>
              </div>

              <span
                className={`incident-badge ${
                  incident.state.toLowerCase()
                }`}
              >
                {incident.state}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [remediationStatus, setRemediationStatus] = useState(null)
  const [incidentHistory, setIncidentHistory] = useState([])
  const [apiError, setApiError] = useState(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(
          'http://127.0.0.1:8000/api/v1/remediation/status'
        )

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`)
        }

        const data = await response.json()

        setRemediationStatus(data)
        const incidentResponse = await fetch(
        'http://127.0.0.1:8000/api/v1/incidents'
      )

      if (!incidentResponse.ok) {
        throw new Error(`Incident API returned ${incidentResponse.status}`)
      }

      const incidentData = await incidentResponse.json()

      setIncidentHistory(incidentData.incidents)
      setApiError(null)
      } catch (error) {
        setApiError(error.message)
      }
    }

    fetchStatus()

    const interval = setInterval(fetchStatus, 5000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
  if (!remediationStatus) {
    return
  }

  const isOpen = remediationStatus.state === 'OPEN'

  setNodes((currentNodes) =>
    currentNodes.map((node) => {
      if (node.id === 'quality') {
        return {
          ...node,
          data: {
            ...node.data,
            label: isOpen
              ? 'Data Quality\nOPEN'
              : 'Data Quality\nHEALTHY',
          },
          style: {
            ...node.style,
            border: isOpen
              ? '2px solid #dc2626'
              : '2px solid #16a34a',
          },
        }
      }

      if (node.id === 'observability') {
        return {
          ...node,
          data: {
            ...node.data,
            label: isOpen
              ? 'Observability\nINCIDENT'
              : 'Observability\nHEALTHY',
          },
          style: {
            ...node.style,
            border: isOpen
              ? '2px solid #dc2626'
              : '2px solid #16a34a',
          },
        }
      }

      return node
    }),
  )
  }, [remediationStatus, setNodes])
  const onConnect = useCallback(
    (connection) => {
      setEdges((currentEdges) => addEdge(connection, currentEdges))
    },
    [setEdges],
  )

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>IceStream</h1>
          <p>Real-Time Lakehouse Observability</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Production Prototype
        </div>
      </header>

      <main className="dashboard">
        <div className="title-section">
          <h2>Pipeline Lineage</h2>
          <p>
            Real-time data flow from checkout events to lakehouse observability.
          </p>
        </div>

        <div className="summary-grid">
          <StatusCard
            title="Checkout Generator"
            value="Active"
            status="LIVE"
          />

          <StatusCard
            title="Kafka Broker"
            value="localhost:9092"
            status="LIVE"
          />

          <StatusCard
            title="Kafka Topic"
            value="checkout-topic"
          />

          <StatusCard
            title="Kafka Partitions"
            value="3"
          />

          <StatusCard
            title="Automated Tests"
            value="58 / 58"
            status="PASSED"
          />
          <StatusCard
            title="Remediation Circuit"
            value={
              remediationStatus
                ? remediationStatus.state
                : 'Loading...'
            }
            status={
              remediationStatus
                ? remediationStatus.state
                : undefined
            }
          />
          <StatusCard
            title="Data Quality"
            value={
              remediationStatus
                ? `${remediationStatus.failed_records} failed / ${remediationStatus.total_records}`
                : 'Loading...'
            }
            status={
              remediationStatus
                ? `${(remediationStatus.error_rate * 100).toFixed(1)}% ERROR`
                : undefined
            }
          />
          
        </div>
        <IncidentCard
          incident={remediationStatus?.incident}
        />

        <IncidentHistory incidents={incidentHistory} />

        <div className="legend">
          <span>
            <span className="legend-dot live"></span>
            Live
          </span>

          <span>
            <span className="legend-dot planned"></span>
            Planned
          </span>
        </div>

        <div className="flow-container">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
            fitViewOptions={{
            padding: 0.2,
            minZoom: 0.6,
            maxZoom: 1.2,
            }}
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </main>
    </div>
  )
}

export default App