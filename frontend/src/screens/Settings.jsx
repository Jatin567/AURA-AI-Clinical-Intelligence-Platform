import { Settings as SettingsIcon } from 'lucide-react';

export default function Settings() {
  return (
    <div>
      <h1 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <SettingsIcon /> Settings
      </h1>

      <div className="card">
        <h3>Account Preferences</h3>
        <p style={{ color: '#9ca3af' }}>Configure your account settings, notifications, and security options.</p>
        
        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '1rem', borderBottom: '1px solid #374151' }}>
            <div>
              <strong>Email Notifications</strong>
              <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>Receive updates about your health assessments.</div>
            </div>
            <input type="checkbox" defaultChecked />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '1rem', borderBottom: '1px solid #374151' }}>
            <div>
              <strong>Data Sharing</strong>
              <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>Allow anonymized data to be used for research.</div>
            </div>
            <input type="checkbox" />
          </div>

          <button className="btn btn-secondary" style={{ width: 'max-content', marginTop: '1rem' }}>Change Password</button>
        </div>
      </div>
    </div>
  );
}
