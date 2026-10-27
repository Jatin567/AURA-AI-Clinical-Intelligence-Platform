import { Link } from 'react-router-dom';
import { Activity, Plus, UserRound } from 'lucide-react';
import { PageTransition } from '../components/PageTransition';
import { useAuth } from '../context/AuthContext';

export default function PatientList() {
  const { user } = useAuth();
  const profiles = Array.isArray(user) ? user : [];

  return (
    <PageTransition>
      <div className="h-full w-full overflow-y-auto bg-background text-foreground">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-8 pt-12">
          <header className="flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight">Patients</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Patient profiles connected to the current authenticated account.
              </p>
            </div>
            <button
              type="button"
              disabled
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-secondary px-4 py-2 text-sm font-medium text-muted-foreground opacity-70"
            >
              <Plus size={16} />
              Add Patient
            </button>
          </header>

          {profiles.length === 0 ? (
            <section className="flex min-h-[320px] flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/50 p-8 text-center">
              <UserRound size={44} className="mb-4 text-muted-foreground" />
              <h2 className="text-lg font-medium">No patient profiles yet</h2>
              <p className="mt-2 max-w-md text-sm text-muted-foreground">
                Authentication is active, but this account does not have a saved clinical profile.
              </p>
            </section>
          ) : (
            <section className="grid gap-4 md:grid-cols-2">
              {profiles.map((profile) => (
                <Link
                  key={profile.patient_id}
                  to={`/workspace/${profile.patient_id}`}
                  className="rounded-xl border border-border bg-card p-5 transition-colors hover:bg-secondary/40"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h2 className="text-lg font-medium">{profile.full_name}</h2>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {profile.date_of_birth || 'DOB not set'} / {profile.biological_sex || 'sex not set'}
                      </p>
                    </div>
                    <Activity size={20} className="text-accent" />
                  </div>
                </Link>
              ))}
            </section>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
