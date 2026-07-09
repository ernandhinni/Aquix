import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, SafeAreaView, StatusBar, Alert, ActivityIndicator,
  FlatList, KeyboardAvoidingView, Platform, Switch,
} from 'react-native';

const BASE_URL = 'http://10.100.100.109:5006';

// ─── THEME ────────────────────────────────────────────────────────
const C = {
  bg:       '#F0F6FF',
  surface:  '#FFFFFF',
  surface2: '#EAF3FF',
  border:   '#C8DDF7',
  border2:  '#A4C8F0',
  aqua:     '#0077CC',
  aqua2:    '#005FA3',
  teal:     '#00A896',
  warn:     '#E07B00',
  danger:   '#D62828',
  success:  '#2D8A4E',
  text:     '#0D1B2A',
  text2:    '#3A5A7A',
  text3:    '#7A9AB8',
  muted:    '#B0C9E0',
  white:    '#FFFFFF',
};

// ─── API HELPERS ──────────────────────────────────────────────────
const api = {
  get: async (path) => {
    const r = await fetch(`${BASE_URL}${path}`);
    return r.json();
  },
  post: async (path, body) => {
    const r = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return r.json();
  },
};

// ─── SHARED COMPONENTS ────────────────────────────────────────────
const Card = ({ children, style }) => (
  <View style={[styles.card, style]}>{children}</View>
);

const Btn = ({ label, onPress, variant = 'primary', style, loading }) => (
  <TouchableOpacity
    style={[styles.btn, variant === 'secondary' && styles.btnSec, style]}
    onPress={onPress} activeOpacity={0.75}>
    {loading
      ? <ActivityIndicator color={variant === 'secondary' ? C.aqua : C.white} size="small" />
      : <Text style={[styles.btnTxt, variant === 'secondary' && styles.btnSecTxt]}>{label}</Text>}
  </TouchableOpacity>
);

const Input = ({ label, value, onChangeText, placeholder, keyboardType = 'default', secureTextEntry }) => (
  <View style={styles.inputWrap}>
    {label ? <Text style={styles.inputLabel}>{label}</Text> : null}
    <TextInput
      style={styles.input}
      value={value}
      onChangeText={onChangeText}
      placeholder={placeholder}
      placeholderTextColor={C.muted}
      keyboardType={keyboardType}
      secureTextEntry={secureTextEntry}
      autoCapitalize="none"
    />
  </View>
);

const Badge = ({ label, color }) => (
  <View style={[styles.badge, { backgroundColor: color + '20', borderColor: color + '60' }]}>
    <Text style={[styles.badgeTxt, { color }]}>{label}</Text>
  </View>
);

const StatRow = ({ label, value, color }) => (
  <View style={styles.statRow}>
    <Text style={styles.statLabel}>{label}</Text>
    <Text style={[styles.statValue, color && { color }]}>{value}</Text>
  </View>
);

const SectionTitle = ({ text }) => (
  <Text style={styles.sectionTitle}>{text}</Text>
);

// ─── SCREENS ──────────────────────────────────────────────────────

// LOGIN
function LoginScreen({ onLogin }) {
  const [tab, setTab] = useState('login');
  const [userType, setUserType] = useState('Citizen');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [zone, setZone] = useState('Koramangala');

  const userTypes = [
    { key: 'Citizen', icon: '🏠' },
    { key: 'Farmer', icon: '🌾' },
    { key: 'Officer', icon: '🏛️' },
  ];

  const zones = ['Koramangala','Indiranagar','Whitefield','Hebbal','Jayanagar','HSR Layout'];

  const handleAuth = () => {
    if (!email || !password) { Alert.alert('Error', 'Please fill all fields'); return; }
    onLogin({ name: name || email.split('@')[0], userType, zone, email });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={C.bg} />
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={styles.loginScroll} keyboardShouldPersistTaps="handled">
          {/* Logo */}
          <View style={styles.logoRow}>
            <View style={styles.logoDrop}><Text style={{ fontSize: 24 }}>💧</Text></View>
            <View>
              <Text style={styles.logoName}>AQUIX</Text>
              <Text style={styles.logoTag}>SMART WATER INTELLIGENCE</Text>
            </View>
          </View>

          <Card style={styles.loginCard}>
            {/* Tabs */}
            <View style={styles.tabRow}>
              {['login','register'].map(t => (
                <TouchableOpacity key={t} style={[styles.tabBtn, tab === t && styles.tabBtnActive]}
                  onPress={() => setTab(t)}>
                  <Text style={[styles.tabBtnTxt, tab === t && styles.tabBtnTxtActive]}>
                    {t === 'login' ? 'Sign In' : 'Register'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* User type */}
            <Text style={styles.inputLabel}>I AM A</Text>
            <View style={styles.userTypeRow}>
              {userTypes.map(u => (
                <TouchableOpacity key={u.key}
                  style={[styles.userTypeBtn, userType === u.key && styles.userTypeBtnActive]}
                  onPress={() => setUserType(u.key)}>
                  <Text style={{ fontSize: 22 }}>{u.icon}</Text>
                  <Text style={[styles.userTypeTxt, userType === u.key && { color: C.aqua }]}>{u.key}</Text>
                </TouchableOpacity>
              ))}
            </View>

            {tab === 'register' && (
              <Input label="FULL NAME" value={name} onChangeText={setName} placeholder="Your name" />
            )}
            <Input label="EMAIL" value={email} onChangeText={setEmail}
              placeholder="email@example.com" keyboardType="email-address" />
            <Input label="PASSWORD" value={password} onChangeText={setPassword}
              placeholder="••••••••" secureTextEntry />

            {/* Zone picker */}
            <Text style={styles.inputLabel}>ZONE</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
              {zones.map(z => (
                <TouchableOpacity key={z}
                  style={[styles.zoneChip, zone === z && styles.zoneChipActive]}
                  onPress={() => setZone(z)}>
                  <Text style={[styles.zoneChipTxt, zone === z && { color: C.aqua }]}>{z}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <Btn label={tab === 'login' ? 'Sign In' : 'Create Account'} onPress={handleAuth} />
          </Card>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// DASHBOARD
function DashboardScreen({ user }) {
  const [data, setData] = useState(null);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/api/dashboard/overview'), api.get('/api/dashboard/zones')])
      .then(([ov, zn]) => { setData(ov); setZones(zn); })
      .catch(() => Alert.alert('Error', 'Could not load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  const riskColor = (r) => r === 'HIGH' ? C.danger : r === 'MEDIUM' ? C.warn : C.success;

  if (loading) return <Loader />;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Dashboard</Text>
        <Text style={styles.pageSubtitle}>Hello, {user.name} 👋</Text>
      </View>

      {/* KPI grid */}
      <View style={styles.kpiGrid}>
        {[
          { label: 'Supply', value: `${data?.total_supply_ml ?? '—'} ML`, icon: '🌊' },
          { label: 'Active Leaks', value: data?.active_leaks ?? '—', icon: '🔴' },
          { label: 'Flood Risk', value: `${data?.flood_risk_percent ?? '—'}%`, icon: '⚠️' },
          { label: 'pH Level', value: data?.water_quality_ph ?? '—', icon: '🧪' },
          { label: 'Usage Today', value: `${data?.usage_today_l ?? '—'} L`, icon: '💧' },
          { label: 'Rainfall', value: `${data?.rainfall_mm ?? '—'} mm`, icon: '🌧️' },
        ].map(k => (
          <Card key={k.label} style={styles.kpiCard}>
            <Text style={styles.kpiIcon}>{k.icon}</Text>
            <Text style={styles.kpiValue}>{k.value}</Text>
            <Text style={styles.kpiLabel}>{k.label}</Text>
          </Card>
        ))}
      </View>

      {/* Zone status */}
      <SectionTitle text="Zone Status" />
      {zones.map(z => (
        <Card key={z.id} style={styles.zoneCard}>
          <View style={styles.zoneRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.zoneName}>{z.name}</Text>
              <Text style={styles.zoneSub}>{z.population.toLocaleString()} residents · {z.pressure_bar} bar</Text>
            </View>
            <View style={{ alignItems: 'flex-end', gap: 4 }}>
              <Badge label={z.risk} color={riskColor(z.risk)} />
              {z.leak && <Badge label="LEAK" color={C.danger} />}
            </View>
          </View>
          {/* Usage bar */}
          <View style={styles.barBg}>
            <View style={[styles.barFill, { width: `${z.usage_pct}%`,
              backgroundColor: z.usage_pct > 85 ? C.danger : z.usage_pct > 65 ? C.warn : C.teal }]} />
          </View>
          <Text style={styles.zonePct}>{z.usage_pct}% capacity</Text>
        </Card>
      ))}
    </ScrollView>
  );
}

// ANOMALY DETECTION
function AnomalyScreen() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [zones, setZones] = useState([
    { zone_id:'Z1', name:'Koramangala', flow_lps:145, consumption_l:85000, pressure_bar:1.7, population:8500 },
    { zone_id:'Z2', name:'Indiranagar', flow_lps:78,  consumption_l:55000, pressure_bar:3.1, population:6200 },
    { zone_id:'Z3', name:'Whitefield',  flow_lps:160, consumption_l:95000, pressure_bar:2.8, population:9100 },
    { zone_id:'Z4', name:'Hebbal',      flow_lps:42,  consumption_l:30000, pressure_bar:3.5, population:4300 },
    { zone_id:'Z5', name:'Jayanagar',   flow_lps:55,  consumption_l:40000, pressure_bar:3.4, population:5600 },
    { zone_id:'Z6', name:'HSR Layout',  flow_lps:88,  consumption_l:65000, pressure_bar:2.7, population:7200 },
  ]);

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/anomaly/detect', { zones });
      setResult(r);
    } catch { Alert.alert('Error', 'Detection failed — is the backend running?'); }
    setLoading(false);
  };

  const sColor = (s) => s === 'CRITICAL' ? C.danger : s === 'HIGH' ? C.warn : s === 'MEDIUM' ? '#C08000' : C.success;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Anomaly Detection</Text>
        <Text style={styles.pageSubtitle}>Ensemble AI · {zones.length} zones</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Zone Sensor Data</Text>
        {zones.map((z, i) => (
          <View key={z.zone_id} style={styles.zoneInputRow}>
            <Text style={styles.zoneInputName}>{z.name}</Text>
            <View style={styles.zoneInputFields}>
              <View style={styles.miniInputWrap}>
                <Text style={styles.miniLabel}>Flow L/s</Text>
                <TextInput style={styles.miniInput}
                  value={String(z.flow_lps)} keyboardType="numeric"
                  onChangeText={v => setZones(prev => prev.map((x,j) => j===i ? {...x, flow_lps:parseFloat(v)||0} : x))} />
              </View>
              <View style={styles.miniInputWrap}>
                <Text style={styles.miniLabel}>Press.</Text>
                <TextInput style={styles.miniInput}
                  value={String(z.pressure_bar)} keyboardType="numeric"
                  onChangeText={v => setZones(prev => prev.map((x,j) => j===i ? {...x, pressure_bar:parseFloat(v)||0} : x))} />
              </View>
            </View>
          </View>
        ))}
        <Btn label="Run Anomaly Detection" onPress={run} loading={loading} style={{ marginTop: 12 }} />
      </Card>

      {result && (
        <>
          {/* Summary */}
          <Card style={{ marginTop: 16 }}>
            <Text style={styles.cardTitle}>Summary</Text>
            <StatRow label="Alert Level" value={result.summary.alert_level}
              color={result.summary.alert_level === 'CRITICAL' ? C.danger : result.summary.alert_level === 'WARNING' ? C.warn : C.success} />
            <StatRow label="Anomalous Zones" value={result.summary.anomalous_zones} />
            <StatRow label="Leak Suspects" value={result.summary.leak_suspects} />
            <StatRow label="Equity Score" value={`${Math.round(result.summary.equity_score * 100)}%`} />
          </Card>

          {/* Zone results */}
          {result.anomalies.map(z => (
            <Card key={z.zone_id} style={[styles.zoneCard, { marginTop: 12 }]}>
              <View style={styles.zoneRow}>
                <Text style={styles.zoneName}>{z.name}</Text>
                <Badge label={z.severity} color={sColor(z.severity)} />
              </View>
              <Badge label={z.anomaly_type} color={z.is_anomaly ? C.danger : C.success}
                style={{ alignSelf: 'flex-start', marginTop: 6 }} />
              <Text style={styles.justification}>{z.justification}</Text>
              <StatRow label="Pressure" value={`${z.metrics.pressure_bar} bar`} />
              <StatRow label="Flow" value={`${z.metrics.flow_lps} L/s`} />
              <StatRow label="Detectors" value={`${z.vote_score}/5`} />
            </Card>
          ))}

          {/* Redistribution */}
          {result.redistribution.transfers.length > 0 && (
            <Card style={{ marginTop: 16 }}>
              <Text style={styles.cardTitle}>Redistribution Plan</Text>
              <Text style={styles.justification}>{result.redistribution.explanation}</Text>
              {result.redistribution.transfers.map((t, i) => (
                <View key={i} style={styles.transferRow}>
                  <Text style={styles.transferTxt}>
                    {t.from_zone} → {t.to_zone}
                  </Text>
                  <Text style={styles.transferVol}>{t.volume_l.toLocaleString()} L</Text>
                </View>
              ))}
            </Card>
          )}
        </>
      )}
    </ScrollView>
  );
}

// LEAK DETECTION
function LeakScreen() {
  const [pressure, setPressure] = useState('3.2');
  const [flow, setFlow] = useState('77');
  const [turbidity, setTurbidity] = useState('45');
  const [zone, setZone] = useState('Koramangala');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/predict/leak', {
        pressure_bar: parseFloat(pressure), flow_lps: parseFloat(flow),
        turbidity: parseFloat(turbidity), zone,
      });
      setResult(r);
    } catch { Alert.alert('Error', 'Request failed'); }
    setLoading(false);
  };

  const vColor = result?.analysis?.verdict === 'LEAK_DETECTED' ? C.danger
    : result?.analysis?.verdict === 'ANOMALY' ? C.warn : C.success;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Leak Detection</Text>
        <Text style={styles.pageSubtitle}>Single sensor analysis</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Sensor Input</Text>
        <Input label="ZONE NAME" value={zone} onChangeText={setZone} placeholder="Zone name" />
        <Input label="PRESSURE (bar)" value={pressure} onChangeText={setPressure} keyboardType="numeric" />
        <Input label="FLOW RATE (L/s)" value={flow} onChangeText={setFlow} keyboardType="numeric" />
        <Input label="TURBIDITY (NTU)" value={turbidity} onChangeText={setTurbidity} keyboardType="numeric" />
        <Btn label="Analyse Sensor" onPress={run} loading={loading} />
      </Card>

      {result && (
        <Card style={{ marginTop: 16 }}>
          <Text style={styles.cardTitle}>Agent Report — {result.zone}</Text>
          <View style={[styles.verdictBox, { borderColor: vColor, backgroundColor: vColor + '15' }]}>
            <Text style={[styles.verdictTxt, { color: vColor }]}>{result.analysis.verdict}</Text>
            <Text style={[styles.verdictSub, { color: vColor }]}>
              Score: {result.analysis.anomaly_score}% · Confidence: {Math.round(result.analysis.probability * 100)}%
            </Text>
          </View>
          <Text style={styles.justification}>{result.alert_message}</Text>
          <StatRow label="Action" value={result.analysis.recommended_action} />
          <StatRow label="Dispatch Team" value={result.dispatch_team ? 'YES' : 'No'} color={result.dispatch_team ? C.danger : C.success} />
        </Card>
      )}
    </ScrollView>
  );
}

// FLOOD PREDICTION
function FloodScreen() {
  const [vals, setVals] = useState({ monsoon_intensity:'5', topography_drainage:'5', river_management:'5', deforestation:'5' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const update = (k, v) => setVals(prev => ({ ...prev, [k]: v }));

  const fields = [
    { key: 'monsoon_intensity', label: 'Monsoon Intensity (1-10)' },
    { key: 'topography_drainage', label: 'Drainage Quality (1-10)' },
    { key: 'river_management', label: 'River Mgmt (1-10)' },
    { key: 'deforestation', label: 'Deforestation Level (1-10)' },
  ];

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/predict/flood', {
        monsoon_intensity: parseFloat(vals.monsoon_intensity),
        topography_drainage: parseFloat(vals.topography_drainage),
        river_management: parseFloat(vals.river_management),
        deforestation: parseFloat(vals.deforestation),
      });
      setResult(r);
    } catch { Alert.alert('Error', 'Request failed'); }
    setLoading(false);
  };

  const rColor = result?.risk_level === 'CRITICAL' ? C.danger : result?.risk_level === 'HIGH' ? C.warn : result?.risk_level === 'MODERATE' ? '#C08000' : C.success;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Flood Prediction</Text>
        <Text style={styles.pageSubtitle}>AI risk assessment</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Parameters</Text>
        {fields.map(f => (
          <Input key={f.key} label={f.label.toUpperCase()} value={vals[f.key]}
            onChangeText={v => update(f.key, v)} keyboardType="numeric" />
        ))}
        <Btn label="Predict Flood Risk" onPress={run} loading={loading} />
      </Card>

      {result && (
        <>
          <Card style={{ marginTop: 16 }}>
            <Text style={styles.cardTitle}>Risk Assessment</Text>
            <View style={[styles.verdictBox, { borderColor: rColor, backgroundColor: rColor + '15' }]}>
              <Text style={[styles.verdictTxt, { color: rColor }]}>{result.risk_level}</Text>
              <Text style={[styles.verdictSub, { color: rColor }]}>
                Probability: {result.flood_probability}%
              </Text>
            </View>
            <StatRow label="Pipeline Stress" value={`${result.pipeline_stress_probability}%`} />
            <StatRow label="Leak Likelihood" value={`${result.leak_likelihood_during_rain}%`} />
          </Card>

          {result.smart_alerts.length > 0 && (
            <Card style={{ marginTop: 12 }}>
              <Text style={styles.cardTitle}>Smart Alerts</Text>
              {result.smart_alerts.map((a, i) => (
                <Text key={i} style={styles.alertItem}>{a}</Text>
              ))}
              <Text style={[styles.justification, { marginTop: 8, color: C.aqua }]}>
                {result.recommendation}
              </Text>
            </Card>
          )}
        </>
      )}
    </ScrollView>
  );
}

// WATER QUALITY
function QualityScreen() {
  const [params, setParams] = useState({ ph: '7.2', solids: '320', turbidity: '4.0' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/predict/potability', {
        ph: parseFloat(params.ph), solids: parseFloat(params.solids), turbidity: parseFloat(params.turbidity),
      });
      setResult(r);
    } catch { Alert.alert('Error', 'Request failed'); }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Water Quality</Text>
        <Text style={styles.pageSubtitle}>Potability check</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Water Parameters</Text>
        <Input label="pH LEVEL" value={params.ph} onChangeText={v => setParams(p => ({...p, ph:v}))} keyboardType="numeric" />
        <Input label="TDS / SOLIDS (mg/L)" value={params.solids} onChangeText={v => setParams(p => ({...p, solids:v}))} keyboardType="numeric" />
        <Input label="TURBIDITY (NTU)" value={params.turbidity} onChangeText={v => setParams(p => ({...p, turbidity:v}))} keyboardType="numeric" />
        <Btn label="Check Potability" onPress={run} loading={loading} />
      </Card>

      {result && (
        <Card style={{ marginTop: 16 }}>
          <View style={[styles.verdictBox, { borderColor: result.potable ? C.success : C.danger,
            backgroundColor: result.potable ? C.success + '15' : C.danger + '15' }]}>
            <Text style={[styles.verdictTxt, { color: result.potable ? C.success : C.danger }]}>
              {result.verdict}
            </Text>
            <Text style={[styles.verdictSub, { color: result.potable ? C.success : C.danger }]}>
              Confidence: {Math.round(result.confidence * 100)}%
            </Text>
          </View>
          {result.issues.length > 0 && result.issues.map((iss, i) => (
            <Text key={i} style={styles.alertItem}>{iss}</Text>
          ))}
          <Text style={styles.justification}>{result.recommendation}</Text>
        </Card>
      )}
    </ScrollView>
  );
}

// FARMER INSIGHTS
function FarmerScreen() {
  const [params, setParams] = useState({ soil_moisture:'50', rain_1h:'0', rain_6h:'5', temperature:'28', crop:'Rice', zone:'Field A' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const crops = ['Rice','Wheat','Maize','Sugarcane','Coffee','Tomato','Cotton','Mustard'];

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/farmer/agent', {
        soil_moisture: parseFloat(params.soil_moisture),
        rain_1h: parseFloat(params.rain_1h),
        rain_6h: parseFloat(params.rain_6h),
        temperature: parseFloat(params.temperature),
        crop: params.crop, zone: params.zone,
      });
      setResult(r);
    } catch { Alert.alert('Error', 'Request failed'); }
    setLoading(false);
  };

  const lrColor = result?.pipe_leak_risk === 'HIGH' ? C.danger : result?.pipe_leak_risk === 'MEDIUM' ? C.warn : C.success;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Farmer Insights</Text>
        <Text style={styles.pageSubtitle}>Smart irrigation & crop AI</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Field Data</Text>
        <Input label="ZONE / FIELD NAME" value={params.zone} onChangeText={v => setParams(p => ({...p, zone:v}))} />
        <Input label="SOIL MOISTURE (%)" value={params.soil_moisture} onChangeText={v => setParams(p => ({...p, soil_moisture:v}))} keyboardType="numeric" />
        <Input label="TEMPERATURE (°C)" value={params.temperature} onChangeText={v => setParams(p => ({...p, temperature:v}))} keyboardType="numeric" />
        <Input label="RAIN LAST 1H (mm)" value={params.rain_1h} onChangeText={v => setParams(p => ({...p, rain_1h:v}))} keyboardType="numeric" />
        <Input label="RAIN LAST 6H (mm)" value={params.rain_6h} onChangeText={v => setParams(p => ({...p, rain_6h:v}))} keyboardType="numeric" />

        <Text style={styles.inputLabel}>CROP</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 14 }}>
          {crops.map(c => (
            <TouchableOpacity key={c}
              style={[styles.zoneChip, params.crop === c && styles.zoneChipActive]}
              onPress={() => setParams(p => ({...p, crop:c}))}>
              <Text style={[styles.zoneChipTxt, params.crop === c && { color: C.aqua }]}>{c}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        <Btn label="Get Irrigation Advice" onPress={run} loading={loading} />
      </Card>

      {result && (
        <>
          <Card style={{ marginTop: 16 }}>
            <Text style={styles.cardTitle}>Pipe Leak Risk</Text>
            <View style={[styles.verdictBox, { borderColor: lrColor, backgroundColor: lrColor + '15' }]}>
              <Text style={[styles.verdictTxt, { color: lrColor }]}>{result.pipe_leak_risk}</Text>
            </View>
            <StatRow label="Moisture Anomaly" value={result.moisture_anomaly ? 'YES ⚠️' : 'No ✅'} />
            <StatRow label="Irrigate Now" value={result.should_irrigate ? 'YES 💧' : 'No'} color={result.should_irrigate ? C.teal : C.text2} />
            <StatRow label="Skip Irrigation" value={result.avoid_irrigation ? 'YES 🌧️' : 'No'} />
            <StatRow label="Water Saved" value={`${result.water_saved_pct}%`} color={C.teal} />
          </Card>

          {result.sensor_alerts.length > 0 && (
            <Card style={{ marginTop: 12 }}>
              <Text style={styles.cardTitle}>Alerts</Text>
              {result.sensor_alerts.map((a, i) => <Text key={i} style={styles.alertItem}>{a}</Text>)}
            </Card>
          )}

          <Card style={{ marginTop: 12 }}>
            <Text style={styles.cardTitle}>Irrigation Schedule</Text>
            {result.irrigation_schedule.map((s, i) => (
              <View key={i} style={styles.scheduleRow}>
                <Text style={styles.scheduleTime}>{s.time}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.scheduleVol}>{s.volume_l} L</Text>
                  <Text style={styles.scheduleNote}>{s.note}</Text>
                </View>
              </View>
            ))}
          </Card>

          <Card style={{ marginTop: 12 }}>
            <Text style={styles.cardTitle}>Management Tips</Text>
            {result.management_tips.map((t, i) => <Text key={i} style={styles.tipItem}>{t}</Text>)}
          </Card>
        </>
      )}
    </ScrollView>
  );
}

// CROP RECOMMENDATION
function CropScreen() {
  const [vals, setVals] = useState({ N:'90', ph:'6.5', rainfall:'200' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/predict/crop', {
        N: parseFloat(vals.N), ph: parseFloat(vals.ph), rainfall: parseFloat(vals.rainfall),
      });
      setResult(r);
    } catch { Alert.alert('Error', 'Request failed'); }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Crop Recommendation</Text>
        <Text style={styles.pageSubtitle}>AI soil analysis</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Soil Parameters</Text>
        <Input label="NITROGEN (N ppm)" value={vals.N} onChangeText={v => setVals(p=>({...p,N:v}))} keyboardType="numeric" />
        <Input label="SOIL pH" value={vals.ph} onChangeText={v => setVals(p=>({...p,ph:v}))} keyboardType="numeric" />
        <Input label="RAINFALL (mm)" value={vals.rainfall} onChangeText={v => setVals(p=>({...p,rainfall:v}))} keyboardType="numeric" />
        <Btn label="Recommend Crop" onPress={run} loading={loading} />
      </Card>

      {result && (
        <Card style={{ marginTop: 16 }}>
          <Text style={styles.cardTitle}>Recommendation</Text>
          <View style={styles.cropMain}>
            <Text style={{ fontSize: 48 }}>{result.emoji}</Text>
            <View style={{ marginLeft: 16 }}>
              <Text style={styles.cropName}>{result.recommended_crop}</Text>
              <Text style={styles.cropMeta}>Match: {result.match_score}/8</Text>
              <Text style={styles.cropMeta}>Season: {result.season}</Text>
              <Text style={styles.cropMeta}>Water: {result.water_requirement}</Text>
            </View>
          </View>
          <Text style={styles.justification}>{result.irrigation_tip}</Text>

          <Text style={[styles.cardTitle, { marginTop: 12 }]}>Alternatives</Text>
          {result.alternatives.map(a => (
            <StatRow key={a.name} label={`${a.emoji} ${a.name}`} value={`Score: ${a.score}`} />
          ))}
        </Card>
      )}
    </ScrollView>
  );
}

// SERVICES / BOOKING
function ServicesScreen({ user }) {
  const [service, setService] = useState('Water Tanker');
  const [address, setAddress] = useState('');
  const [date, setDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [ticket, setTicket] = useState(null);

  const services = ['Water Tanker','Pipeline Repair','Quality Test','Meter Reading','Rain Harvesting'];

  const book = async () => {
    if (!address || !date) { Alert.alert('Error', 'Fill address and date'); return; }
    setLoading(true);
    try {
      const r = await api.post('/api/services/book', {
        service, address, date, user_type: user.userType,
        zone: user.zone, name: user.name, email: user.email,
      });
      setTicket(r);
    } catch { Alert.alert('Error', 'Booking failed'); }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Services</Text>
        <Text style={styles.pageSubtitle}>Book water services</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Select Service</Text>
        {services.map(s => (
          <TouchableOpacity key={s}
            style={[styles.serviceBtn, service === s && styles.serviceBtnActive]}
            onPress={() => setService(s)}>
            <Text style={[styles.serviceBtnTxt, service === s && { color: C.aqua, fontWeight: '700' }]}>{s}</Text>
            {service === s && <Text style={{ color: C.aqua }}>✓</Text>}
          </TouchableOpacity>
        ))}

        <Input label="DELIVERY ADDRESS" value={address} onChangeText={setAddress} placeholder="Enter address" />
        <Input label="PREFERRED DATE (DD/MM/YYYY)" value={date} onChangeText={setDate} placeholder="e.g. 15/07/2025" />
        <Btn label="Book Service" onPress={book} loading={loading} />
      </Card>

      {ticket && (
        <Card style={{ marginTop: 16, borderColor: C.success, borderWidth: 1 }}>
          <Text style={[styles.cardTitle, { color: C.success }]}>✅ Booking Confirmed!</Text>
          <StatRow label="Ticket ID" value={ticket.ticket_id} color={C.aqua} />
          <StatRow label="Service" value={service} />
          <StatRow label="Zone" value={user.zone} />
        </Card>
      )}
    </ScrollView>
  );
}

// COMPLAINTS
function ComplaintsScreen({ user }) {
  const [type, setType] = useState('Low Pressure');
  const [description, setDescription] = useState('');
  const [trackId, setTrackId] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [trackResult, setTrackResult] = useState(null);

  const types = ['Low Pressure','Water Contamination','No Supply','Pipeline Leak','High Bill','Other'];

  const submit = async () => {
    if (!description) { Alert.alert('Error', 'Enter complaint description'); return; }
    setLoading(true);
    try {
      const r = await api.post('/api/complaints/submit', {
        type, description, zone: user.zone, name: user.name, email: user.email,
      });
      setSubmitResult(r);
      setDescription('');
    } catch { Alert.alert('Error', 'Submission failed'); }
    setLoading(false);
  };

  const track = async () => {
    if (!trackId) { Alert.alert('Error', 'Enter ticket ID'); return; }
    try {
      const r = await api.get(`/api/complaints/status/${trackId}`);
      setTrackResult(r);
    } catch { Alert.alert('Error', 'Not found'); }
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Complaints</Text>
        <Text style={styles.pageSubtitle}>File & track issues</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>File a Complaint</Text>
        <Text style={styles.inputLabel}>ISSUE TYPE</Text>
        <View style={styles.typeGrid}>
          {types.map(t => (
            <TouchableOpacity key={t}
              style={[styles.typeChip, type === t && styles.typeChipActive]}
              onPress={() => setType(t)}>
              <Text style={[styles.typeChipTxt, type === t && { color: C.aqua }]}>{t}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <Input label="DESCRIPTION" value={description} onChangeText={setDescription}
          placeholder="Describe your issue..." />
        <Btn label="Submit Complaint" onPress={submit} loading={loading} />
      </Card>

      {submitResult && (
        <Card style={{ marginTop: 16, borderColor: C.success, borderWidth: 1 }}>
          <Text style={[styles.cardTitle, { color: C.success }]}>✅ Complaint Filed</Text>
          <StatRow label="Ticket ID" value={submitResult.ticket_id} color={C.aqua} />
          <Text style={styles.justification}>Save this ID to track your complaint.</Text>
        </Card>
      )}

      <Card style={{ marginTop: 16 }}>
        <Text style={styles.cardTitle}>Track Complaint</Text>
        <Input label="TICKET ID (e.g. AQ-1001)" value={trackId} onChangeText={setTrackId} placeholder="AQ-XXXX" />
        <Btn label="Track Status" onPress={track} variant="secondary" />
        {trackResult && (
          <View style={{ marginTop: 12 }}>
            <StatRow label="Status" value={trackResult.status}
              color={trackResult.status === 'Not Found' ? C.danger : C.success} />
          </View>
        )}
      </Card>
    </ScrollView>
  );
}

// DEMAND PREDICTION
function DemandScreen() {
  const [vals, setVals] = useState({ temperature:'28', humidity:'65', population_density:'12', rainfall:'45', user_type:'Residential' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const uTypes = ['Residential','Agricultural','Industrial','Commercial'];
  const dColor = result?.demand_level === 'High' ? C.danger : result?.demand_level === 'Moderate' ? C.warn : C.success;

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.post('/api/predict/demand', {
        temperature: parseFloat(vals.temperature),
        humidity: parseFloat(vals.humidity),
        population_density: parseFloat(vals.population_density),
        rainfall: parseFloat(vals.rainfall),
        user_type: vals.user_type,
      });
      setResult(r);
    } catch { Alert.alert('Error', 'Request failed'); }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 32 }}>
      <View style={styles.pageHeader}>
        <Text style={styles.pageTitle}>Demand Forecast</Text>
        <Text style={styles.pageSubtitle}>ML-based water demand prediction</Text>
      </View>

      <Card>
        <Text style={styles.cardTitle}>Input Parameters</Text>
        <Input label="TEMPERATURE (°C)" value={vals.temperature} onChangeText={v=>setVals(p=>({...p,temperature:v}))} keyboardType="numeric" />
        <Input label="HUMIDITY (%)" value={vals.humidity} onChangeText={v=>setVals(p=>({...p,humidity:v}))} keyboardType="numeric" />
        <Input label="POPULATION DENSITY" value={vals.population_density} onChangeText={v=>setVals(p=>({...p,population_density:v}))} keyboardType="numeric" />
        <Input label="RAINFALL (mm)" value={vals.rainfall} onChangeText={v=>setVals(p=>({...p,rainfall:v}))} keyboardType="numeric" />

        <Text style={styles.inputLabel}>USER TYPE</Text>
        <View style={styles.typeGrid}>
          {uTypes.map(t => (
            <TouchableOpacity key={t}
              style={[styles.typeChip, vals.user_type === t && styles.typeChipActive]}
              onPress={() => setVals(p => ({...p, user_type:t}))}>
              <Text style={[styles.typeChipTxt, vals.user_type === t && { color: C.aqua }]}>{t}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <Btn label="Predict Demand" onPress={run} loading={loading} />
      </Card>

      {result && (
        <Card style={{ marginTop: 16 }}>
          <Text style={styles.cardTitle}>Prediction Result</Text>
          <View style={[styles.verdictBox, { borderColor: dColor, backgroundColor: dColor + '15' }]}>
            <Text style={[styles.verdictTxt, { color: dColor }]}>{result.demand_level} Demand</Text>
            <Text style={[styles.verdictSub, { color: dColor }]}>
              {result.predicted_demand_l_day.toLocaleString()} L/day
            </Text>
          </View>
          <StatRow label="Confidence" value={`${Math.round(result.confidence * 100)}%`} />
          <StatRow label="Model" value={result.model} />
          <Text style={[styles.cardTitle, { marginTop: 12 }]}>Breakdown</Text>
          {Object.entries(result.breakdown).map(([k, v]) => (
            <StatRow key={k} label={k.replace(/_/g, ' ')} value={`${v} L`} />
          ))}
        </Card>
      )}
    </ScrollView>
  );
}

// CHATBOT
function ChatScreen() {
  const [messages, setMessages] = useState([
    { id: '0', role: 'bot', text: '💧 Hi! I\'m AquaSphere. Ask me about leaks, water quality, floods, or irrigation.' }
  ]);
  const [input, setInput] = useState('');
  const [lang, setLang] = useState('en');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef();

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { id: Date.now().toString(), role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    const q = input; setInput(''); setLoading(true);
    try {
      const r = await api.post('/api/chat', { message: q, language: lang });
      setMessages(prev => [...prev, { id: Date.now().toString() + 'b', role: 'bot', text: r.response }]);
    } catch {
      setMessages(prev => [...prev, { id: Date.now().toString() + 'e', role: 'bot', text: '⚠️ Could not reach server.' }]);
    }
    setLoading(false);
    setTimeout(() => scrollRef.current?.scrollToEnd(), 100);
  };

  const quickQ = ['Active leaks?', 'Flood risk today?', 'Is water safe to drink?', 'Tanker booking?'];
  const langOpts = [{ k:'en', l:'EN' }, { k:'kn', l:'ಕನ್ನಡ' }, { k:'hi', l:'हिन्दी' }];

  return (
    <SafeAreaView style={{ flex:1, backgroundColor: C.bg }}>
      {/* Lang switcher */}
      <View style={styles.chatLangRow}>
        {langOpts.map(l => (
          <TouchableOpacity key={l.k}
            style={[styles.langBtn, lang === l.k && styles.langBtnActive]}
            onPress={() => setLang(l.k)}>
            <Text style={[styles.langBtnTxt, lang === l.k && { color: C.white }]}>{l.l}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView ref={scrollRef} style={styles.chatMessages}
        contentContainerStyle={{ padding: 16, paddingBottom: 8 }}>
        {messages.map(m => (
          <View key={m.id} style={[styles.bubble, m.role === 'user' ? styles.bubbleUser : styles.bubbleBot]}>
            <Text style={[styles.bubbleTxt, m.role === 'user' && { color: C.white }]}>{m.text}</Text>
          </View>
        ))}
        {loading && (
          <View style={styles.bubbleBot}>
            <ActivityIndicator size="small" color={C.aqua} />
          </View>
        )}
      </ScrollView>

      {/* Quick questions */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false}
        style={styles.quickRow} contentContainerStyle={{ paddingHorizontal: 12 }}>
        {quickQ.map(q => (
          <TouchableOpacity key={q} style={styles.quickChip} onPress={() => { setInput(q); }}>
            <Text style={styles.quickChipTxt}>{q}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={styles.chatInputRow}>
          <TextInput
            style={styles.chatInput}
            value={input} onChangeText={setInput}
            placeholder="Ask AquaSphere..." placeholderTextColor={C.muted}
            onSubmitEditing={send}
          />
          <TouchableOpacity style={styles.sendBtn} onPress={send}>
            <Text style={{ color: C.white, fontSize: 18 }}>➤</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─── LOADER ───────────────────────────────────────────────────────
function Loader() {
  return (
    <View style={styles.loader}>
      <ActivityIndicator size="large" color={C.aqua} />
      <Text style={styles.loaderTxt}>Loading…</Text>
    </View>
  );
}

// ─── MAIN APP ────────────────────────────────────────────────────
const TABS = [
  { key:'dashboard',  label:'Home',    icon:'🏠' },
  { key:'anomaly',    label:'Anomaly', icon:'🔍' },
  { key:'leak',       label:'Leak',    icon:'🔴' },
  { key:'flood',      label:'Flood',   icon:'🌊' },
  { key:'quality',    label:'Quality', icon:'🧪' },
  { key:'farmer',     label:'Farm',    icon:'🌾' },
  { key:'crop',       label:'Crop',    icon:'🌽' },
  { key:'demand',     label:'Demand',  icon:'📊' },
  { key:'services',   label:'Service', icon:'🚛' },
  { key:'complaints', label:'Issues',  icon:'📋' },
  { key:'chat',       label:'AI Chat', icon:'💬' },
];

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  if (!user) return <LoginScreen onLogin={setUser} />;

  const renderScreen = () => {
    switch (activeTab) {
      case 'dashboard':  return <DashboardScreen user={user} />;
      case 'anomaly':    return <AnomalyScreen />;
      case 'leak':       return <LeakScreen />;
      case 'flood':      return <FloodScreen />;
      case 'quality':    return <QualityScreen />;
      case 'farmer':     return <FarmerScreen />;
      case 'crop':       return <CropScreen />;
      case 'demand':     return <DemandScreen />;
      case 'services':   return <ServicesScreen user={user} />;
      case 'complaints': return <ComplaintsScreen user={user} />;
      case 'chat':       return <ChatScreen />;
      default:           return <DashboardScreen user={user} />;
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.bg }}>
      <StatusBar barStyle="dark-content" backgroundColor={C.bg} />

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={{ fontSize: 20 }}>💧</Text>
          <Text style={styles.headerTitle}>AQUIX</Text>
        </View>
        <TouchableOpacity onPress={() => setUser(null)}>
          <Text style={styles.logoutBtn}>{user.name.split(' ')[0]} · Sign Out</Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <View style={{ flex: 1 }}>{renderScreen()}</View>

      {/* Bottom Nav */}
      <View style={styles.bottomNav}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.bottomNavInner}>
          {TABS.map(t => (
            <TouchableOpacity key={t.key}
              style={[styles.navItem, activeTab === t.key && styles.navItemActive]}
              onPress={() => setActiveTab(t.key)}>
              <Text style={styles.navIcon}>{t.icon}</Text>
              <Text style={[styles.navLabel, activeTab === t.key && { color: C.aqua, fontWeight:'700' }]}>
                {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

// ─── STYLES ───────────────────────────────────────────────────────
const styles = StyleSheet.create({
  safeArea:       { flex:1, backgroundColor: C.bg },
  screen:         { flex:1, backgroundColor: C.bg, paddingHorizontal:16 },

  // Header
  header:         { flexDirection:'row', alignItems:'center', justifyContent:'space-between',
                    paddingHorizontal:16, paddingVertical:12, backgroundColor:C.white,
                    borderBottomWidth:1, borderBottomColor:C.border },
  headerLeft:     { flexDirection:'row', alignItems:'center', gap:8 },
  headerTitle:    { fontSize:18, fontWeight:'800', color:C.aqua, letterSpacing:2 },
  logoutBtn:      { fontSize:12, color:C.text3 },

  // Page header
  pageHeader:     { paddingTop:20, paddingBottom:12 },
  pageTitle:      { fontSize:22, fontWeight:'800', color:C.text },
  pageSubtitle:   { fontSize:13, color:C.text3, marginTop:2 },

  // Card
  card:           { backgroundColor:C.white, borderRadius:16, padding:16, marginBottom:4,
                    borderWidth:1, borderColor:C.border,
                    shadowColor:'#000', shadowOffset:{width:0,height:2}, shadowOpacity:0.06, shadowRadius:8, elevation:2 },
  cardTitle:      { fontSize:14, fontWeight:'700', color:C.text2, marginBottom:12, textTransform:'uppercase', letterSpacing:0.5 },

  // Button
  btn:            { backgroundColor:C.aqua, borderRadius:12, paddingVertical:14, alignItems:'center', marginTop:4 },
  btnSec:         { backgroundColor:'transparent', borderWidth:1.5, borderColor:C.aqua },
  btnTxt:         { color:C.white, fontWeight:'700', fontSize:14, letterSpacing:0.3 },
  btnSecTxt:      { color:C.aqua, fontWeight:'700', fontSize:14 },

  // Input
  inputWrap:      { marginBottom:14 },
  inputLabel:     { fontSize:10, fontWeight:'700', color:C.text3, letterSpacing:1.5, marginBottom:6, textTransform:'uppercase' },
  input:          { backgroundColor:C.surface2, borderWidth:1.5, borderColor:C.border, borderRadius:10,
                    paddingHorizontal:14, paddingVertical:11, color:C.text, fontSize:14 },

  // Badge
  badge:          { borderRadius:6, paddingHorizontal:8, paddingVertical:3, borderWidth:1, alignSelf:'flex-start' },
  badgeTxt:       { fontSize:10, fontWeight:'700', letterSpacing:0.5 },

  // StatRow
  statRow:        { flexDirection:'row', justifyContent:'space-between', paddingVertical:7,
                    borderBottomWidth:1, borderBottomColor:C.surface2 },
  statLabel:      { fontSize:13, color:C.text2 },
  statValue:      { fontSize:13, fontWeight:'600', color:C.text },

  // Section title
  sectionTitle:   { fontSize:13, fontWeight:'700', color:C.text2, textTransform:'uppercase',
                    letterSpacing:1, marginTop:20, marginBottom:10 },

  // Login
  loginScroll:    { flexGrow:1, justifyContent:'center', padding:20 },
  logoRow:        { flexDirection:'row', alignItems:'center', gap:14, marginBottom:28, justifyContent:'center' },
  logoDrop:       { width:52, height:52, backgroundColor:C.aqua, borderRadius:16,
                    alignItems:'center', justifyContent:'center' },
  logoName:       { fontSize:30, fontWeight:'900', color:C.aqua, letterSpacing:4 },
  logoTag:        { fontSize:9, color:C.text3, letterSpacing:2 },
  loginCard:      { borderRadius:20, padding:22 },
  tabRow:         { flexDirection:'row', backgroundColor:C.surface2, borderRadius:10, padding:4, marginBottom:20 },
  tabBtn:         { flex:1, paddingVertical:10, alignItems:'center', borderRadius:7 },
  tabBtnActive:   { backgroundColor:C.aqua },
  tabBtnTxt:      { fontSize:13, fontWeight:'600', color:C.text3 },
  tabBtnTxtActive:{ color:C.white },
  userTypeRow:    { flexDirection:'row', gap:8, marginBottom:16 },
  userTypeBtn:    { flex:1, alignItems:'center', paddingVertical:12, backgroundColor:C.surface2,
                    borderRadius:10, borderWidth:1.5, borderColor:C.border, gap:4 },
  userTypeBtnActive:{ borderColor:C.aqua, backgroundColor: C.aqua + '15' },
  userTypeTxt:    { fontSize:11, fontWeight:'600', color:C.text3 },
  zoneChip:       { paddingHorizontal:14, paddingVertical:8, backgroundColor:C.surface2,
                    borderRadius:20, borderWidth:1.5, borderColor:C.border, marginRight:8 },
  zoneChipActive: { borderColor:C.aqua, backgroundColor: C.aqua + '15' },
  zoneChipTxt:    { fontSize:12, color:C.text3 },

  // KPI
  kpiGrid:        { flexDirection:'row', flexWrap:'wrap', gap:10, marginBottom:4 },
  kpiCard:        { width:'30%', flexGrow:1, alignItems:'center', paddingVertical:14 },
  kpiIcon:        { fontSize:22, marginBottom:6 },
  kpiValue:       { fontSize:15, fontWeight:'800', color:C.text },
  kpiLabel:       { fontSize:10, color:C.text3, marginTop:2, textAlign:'center' },

  // Zone card
  zoneCard:       { marginBottom:10 },
  zoneRow:        { flexDirection:'row', alignItems:'flex-start', justifyContent:'space-between', marginBottom:8 },
  zoneName:       { fontSize:15, fontWeight:'700', color:C.text },
  zoneSub:        { fontSize:11, color:C.text3, marginTop:2 },
  zonePct:        { fontSize:11, color:C.text3, textAlign:'right', marginTop:4 },
  barBg:          { height:6, backgroundColor:C.surface2, borderRadius:3, overflow:'hidden' },
  barFill:        { height:'100%', borderRadius:3 },

  // Anomaly zone input
  zoneInputRow:   { flexDirection:'row', alignItems:'center', paddingVertical:8,
                    borderBottomWidth:1, borderBottomColor:C.surface2 },
  zoneInputName:  { flex:1, fontSize:12, fontWeight:'600', color:C.text2 },
  zoneInputFields:{ flexDirection:'row', gap:8 },
  miniInputWrap:  { alignItems:'center' },
  miniLabel:      { fontSize:9, color:C.text3, marginBottom:3 },
  miniInput:      { width:58, borderWidth:1, borderColor:C.border, borderRadius:7,
                    padding:6, textAlign:'center', fontSize:12, color:C.text, backgroundColor:C.surface2 },

  // Verdict box
  verdictBox:     { borderRadius:12, borderWidth:1.5, padding:16, alignItems:'center', marginBottom:14 },
  verdictTxt:     { fontSize:20, fontWeight:'800' },
  verdictSub:     { fontSize:13, marginTop:4 },

  // Justification
  justification:  { fontSize:13, color:C.text2, lineHeight:20, marginTop:4 },

  // Transfer row
  transferRow:    { flexDirection:'row', justifyContent:'space-between', alignItems:'center',
                    paddingVertical:8, borderBottomWidth:1, borderBottomColor:C.surface2 },
  transferTxt:    { fontSize:13, color:C.text2 },
  transferVol:    { fontSize:13, fontWeight:'700', color:C.aqua },

  // Alert item
  alertItem:      { fontSize:13, color:C.text2, paddingVertical:5, lineHeight:19 },

  // Schedule
  scheduleRow:    { flexDirection:'row', alignItems:'flex-start', paddingVertical:8,
                    borderBottomWidth:1, borderBottomColor:C.surface2 },
  scheduleTime:   { width:80, fontSize:12, fontWeight:'700', color:C.aqua, paddingTop:2 },
  scheduleVol:    { fontSize:13, fontWeight:'700', color:C.text },
  scheduleNote:   { fontSize:11, color:C.text3, marginTop:2 },

  // Tip
  tipItem:        { fontSize:12, color:C.text2, paddingVertical:5, lineHeight:18 },

  // Crop
  cropMain:       { flexDirection:'row', alignItems:'center', marginBottom:12, paddingVertical:8 },
  cropName:       { fontSize:22, fontWeight:'800', color:C.text },
  cropMeta:       { fontSize:12, color:C.text3, marginTop:3 },

  // Service btn
  serviceBtn:     { flexDirection:'row', justifyContent:'space-between', paddingVertical:12,
                    paddingHorizontal:4, borderBottomWidth:1, borderBottomColor:C.surface2 },
  serviceBtnActive:{ },
  serviceBtnTxt:  { fontSize:14, color:C.text2 },

  // Type grid
  typeGrid:       { flexDirection:'row', flexWrap:'wrap', gap:8, marginBottom:14 },
  typeChip:       { paddingHorizontal:12, paddingVertical:7, backgroundColor:C.surface2,
                    borderRadius:20, borderWidth:1.5, borderColor:C.border },
  typeChipActive: { borderColor:C.aqua, backgroundColor: C.aqua + '15' },
  typeChipTxt:    { fontSize:12, color:C.text3, fontWeight:'600' },

  // Chat
  chatLangRow:    { flexDirection:'row', gap:8, padding:12, backgroundColor:C.white,
                    borderBottomWidth:1, borderBottomColor:C.border },
  langBtn:        { paddingHorizontal:14, paddingVertical:7, borderRadius:20, backgroundColor:C.surface2, borderWidth:1, borderColor:C.border },
  langBtnActive:  { backgroundColor:C.aqua, borderColor:C.aqua },
  langBtnTxt:     { fontSize:12, color:C.text3, fontWeight:'600' },
  chatMessages:   { flex:1 },
  bubble:         { maxWidth:'80%', borderRadius:14, padding:12, marginVertical:4 },
  bubbleBot:      { backgroundColor:C.white, borderColor:C.border, borderWidth:1, alignSelf:'flex-start', borderBottomLeftRadius:4 },
  bubbleUser:     { backgroundColor:C.aqua, alignSelf:'flex-end', borderBottomRightRadius:4 },
  bubbleTxt:      { fontSize:14, color:C.text, lineHeight:20 },
  quickRow:       { backgroundColor:C.white, borderTopWidth:1, borderTopColor:C.border, paddingVertical:8 },
  quickChip:      { paddingHorizontal:12, paddingVertical:7, backgroundColor:C.surface2, borderRadius:16,
                    borderWidth:1, borderColor:C.border, marginRight:8 },
  quickChipTxt:   { fontSize:12, color:C.text2 },
  chatInputRow:   { flexDirection:'row', padding:12, gap:10, backgroundColor:C.white,
                    borderTopWidth:1, borderTopColor:C.border },
  chatInput:      { flex:1, backgroundColor:C.surface2, borderRadius:22, paddingHorizontal:16, paddingVertical:10,
                    color:C.text, fontSize:14, borderWidth:1, borderColor:C.border },
  sendBtn:        { width:44, height:44, borderRadius:22, backgroundColor:C.aqua, alignItems:'center', justifyContent:'center' },

  // Nav
  bottomNav:      { backgroundColor:C.white, borderTopWidth:1, borderTopColor:C.border, paddingBottom:6 },
  bottomNavInner: { paddingHorizontal:6, paddingTop:8, gap:4 },
  navItem:        { alignItems:'center', paddingHorizontal:10, paddingVertical:4, borderRadius:10, minWidth:56 },
  navItemActive:  { backgroundColor: C.aqua + '15' },
  navIcon:        { fontSize:20, marginBottom:2 },
  navLabel:       { fontSize:10, color:C.text3, fontWeight:'500' },

  // Loader
  loader:         { flex:1, alignItems:'center', justifyContent:'center', gap:12 },
  loaderTxt:      { color:C.text3, fontSize:14 },
});
