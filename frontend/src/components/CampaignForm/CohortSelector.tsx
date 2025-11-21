import React, { useState, useMemo } from 'react';
import { Search, X, Users } from 'lucide-react';
import type { Cohort } from '@/types/campaign';

interface CohortSelectorProps {
  cohorts: Cohort[];
  selectedCohorts: string[];
  onChange: (value: string[]) => void;
  error?: string;
}

export const CohortSelector: React.FC<CohortSelectorProps> = ({
  cohorts = [],
  selectedCohorts = [],
  onChange,
  error,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const getCohortId = (cohort: Cohort) => {
    return cohort.id || '';
  };

  const getCohortName = (cohort: Cohort) => {
    return cohort.name || (cohort as any).cohort_name || '';
  };

  const filteredCohorts = useMemo(() => {
    return cohorts.filter(cohort => {
      const cohortName = getCohortName(cohort);
      return cohortName?.toLowerCase().includes(searchTerm.toLowerCase());
    });
  }, [cohorts, searchTerm]);

  const selectedCohortObjects = useMemo(() => {
    return cohorts.filter(cohort => {
      const cohortId = getCohortId(cohort);
      return selectedCohorts.includes(cohortId);
    });
  }, [cohorts, selectedCohorts]);

  const toggleCohort = (cohort: Cohort) => {
    const cohortId = getCohortId(cohort);
    if (selectedCohorts.includes(cohortId)) {
      onChange(selectedCohorts.filter(c => c !== cohortId));
    } else {
      onChange([...selectedCohorts, cohortId]);
    }
  };

  const removeCohort = (cohortId: string) => {
    onChange(selectedCohorts.filter(c => c !== cohortId));
  };

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
        <input
          type="text"
          placeholder="Search customer segments..."
          className="w-full bg-zinc-900/50 border border-zinc-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Selected Cohorts Badges */}
      {selectedCohorts.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedCohortObjects.map((cohort) => {
            const cohortId = getCohortId(cohort);
            const cohortName = getCohortName(cohort);
            return (
              <div
                key={cohortId}
                className="inline-flex items-center gap-2 bg-primary/10 text-primary border border-primary/30 text-xs font-bold px-3 py-1.5 rounded-md tracking-wide uppercase"
              >
                <span>{cohortName}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeCohort(cohortId);
                  }}
                  className="hover:text-white focus:outline-none transition-colors"
                  aria-label={`Remove ${cohortName}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Available Cohorts Grid */}
      <div className="border border-zinc-800 rounded-lg bg-black/20 max-h-[320px] overflow-y-auto p-2">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {filteredCohorts.map((cohort) => {
            const cohortId = getCohortId(cohort);
            const cohortName = getCohortName(cohort);
            const isSelected = selectedCohorts.includes(cohortId);
            return (
              <button
                key={cohortId}
                type="button"
                onClick={() => toggleCohort(cohort)}
                className={`
                  flex items-start gap-3 p-3 rounded-md transition-all text-left border group
                  ${isSelected
                    ? 'border-primary/50 bg-primary/5 shadow-[inset_0_0_10px_rgba(0,166,81,0.1)]'
                    : 'border-transparent hover:bg-white/5 hover:border-white/5'
                  }
                `}
              >
                <div className={`mt-0.5 w-4 h-4 rounded flex items-center justify-center border ${isSelected ? 'bg-primary border-primary' : 'border-zinc-600 bg-zinc-900 group-hover:border-zinc-500'}`}>
                  {isSelected && <Users className="w-2.5 h-2.5 text-white" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-medium ${isSelected ? 'text-primary' : 'text-zinc-300 group-hover:text-white'}`}>
                    {cohortName}
                  </div>
                  {cohort.description && (
                    <div className="text-xs text-zinc-500 mt-1 line-clamp-2 leading-relaxed">
                      {cohort.description}
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
        {filteredCohorts.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-500">
            <Search className="w-8 h-8 mb-3 opacity-20" />
            <p className="text-sm">No cohorts found matching your search</p>
          </div>
        )}
      </div>

      {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
    </div>
  );
};
