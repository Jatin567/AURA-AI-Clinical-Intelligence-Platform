import { useAuth } from '../context/AuthContext';
import { User, Activity, FileText, AlertTriangle, Edit, Settings } from 'lucide-react';
import { PageTransition } from '../components/PageTransition';
import { motion } from 'framer-motion';

export default function Profile() {
  const { user } = useAuth();
  
  if (!user || user.length === 0) {
    return (
      <PageTransition>
        <div className="flex h-full items-center justify-center bg-background text-muted-foreground p-8">
          <div className="text-center">
            <User size={48} className="mx-auto mb-4 opacity-50" />
            <h2 className="text-lg font-medium text-foreground">No Profile Found</h2>
            <p className="mt-1">Please log in to view your patient profile.</p>
          </div>
        </div>
      </PageTransition>
    );
  }
  
  const profile = user[0];

  return (
    <PageTransition>
      <div className="flex h-full w-full bg-background text-foreground overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto w-full p-8 pt-12 space-y-8">
          
          {/* Header Section */}
          <div className="flex items-center justify-between border-b border-border pb-6">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-full bg-secondary border border-border flex items-center justify-center text-3xl font-semibold text-foreground">
                {profile.first_name?.[0]}{profile.last_name?.[0]}
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-foreground">{profile.full_name || `${profile.first_name} ${profile.last_name}`}</h1>
                <p className="text-sm font-mono text-muted-foreground mt-1">
                  ID: {profile.patient_id} • Status: Active
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-secondary hover:bg-secondary/80 border border-border rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                <Edit size={16} /> Edit Profile
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Basic Information */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <div className="bg-card border border-border rounded-xl p-6 h-full shadow-sm">
                <h3 className="text-sm font-mono uppercase tracking-wide text-muted-foreground mb-6 flex items-center gap-2">
                  <User size={16} /> Basic Information
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-1 border-b border-border/50">
                    <span className="text-sm text-muted-foreground">Full Name</span>
                    <span className="text-sm font-medium text-foreground">{profile.full_name || `${profile.first_name} ${profile.last_name}`}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-border/50">
                    <span className="text-sm text-muted-foreground">Date of Birth</span>
                    <span className="text-sm font-medium text-foreground">{profile.date_of_birth || 'Not Specified'}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-border/50">
                    <span className="text-sm text-muted-foreground">Biological Sex</span>
                    <span className="text-sm font-medium text-foreground capitalize">{profile.biological_sex || 'Not Specified'}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-border/50">
                    <span className="text-sm text-muted-foreground">Contact</span>
                    <span className="text-sm font-medium text-foreground">Registered on File</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Medical History */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <div className="bg-card border border-border rounded-xl p-6 h-full shadow-sm">
                <h3 className="text-sm font-mono uppercase tracking-wide text-muted-foreground mb-6 flex items-center gap-2">
                  <Activity size={16} /> Medical History
                </h3>
                {profile.medical_history?.chronic_conditions?.length > 0 ? (
                  <ul className="space-y-2">
                    {profile.medical_history.chronic_conditions.map((condition, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm text-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                        {condition}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-muted-foreground italic flex items-center gap-2">
                    No chronic conditions reported.
                  </div>
                )}
              </div>
            </motion.div>

            {/* Medications */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <div className="bg-card border border-border rounded-xl p-6 h-full shadow-sm">
                <h3 className="text-sm font-mono uppercase tracking-wide text-muted-foreground mb-6 flex items-center gap-2">
                  <FileText size={16} /> Current Medications
                </h3>
                {profile.medications?.current_medications?.length > 0 ? (
                  <ul className="space-y-2">
                    {profile.medications.current_medications.map((med, i) => (
                      <li key={i} className="flex items-center justify-between text-sm text-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50">
                        <div className="flex items-center gap-3">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                          {med}
                        </div>
                        <span className="text-xs font-mono text-muted-foreground">Active</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-muted-foreground italic">
                    No current medications.
                  </div>
                )}
              </div>
            </motion.div>
            
            {/* Allergies */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <div className="bg-card border border-border rounded-xl p-6 h-full shadow-sm">
                <h3 className="text-sm font-mono uppercase tracking-wide text-muted-foreground mb-6 flex items-center gap-2">
                  <AlertTriangle size={16} /> Allergies
                </h3>
                {profile.allergies?.allergies?.length > 0 ? (
                  <ul className="space-y-2">
                    {profile.allergies.allergies.map((allergy, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm text-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                        {allergy}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-muted-foreground italic">
                    No known allergies.
                  </div>
                )}
              </div>
            </motion.div>
          </div>
          
        </div>
      </div>
    </PageTransition>
  );
}
