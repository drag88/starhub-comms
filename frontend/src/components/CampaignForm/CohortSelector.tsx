import React, { useState, useMemo } from 'react';
import type { Cohort } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';

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
    <div>
      {selectedCohorts.length > 0 && (
        <div className="flex items-center justify-end mb-2">
          <span className="text-sm text-gray-600">
            {selectedCohorts.length} selected
          </span>
        </div>
      )}

      {/* Selected Cohorts - Compact Badges */}
      {selectedCohorts.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3 pb-2 border-b border-gray-200">
          {selectedCohortObjects.map((cohort) => {
            const cohortId = getCohortId(cohort);
            const cohortName = getCohortName(cohort);
            return (
              <div
                key={cohortId}
                className="inline-flex items-center gap-1.5 bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded"
              >
                <span>{cohortName}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeCohort(cohortId);
                  }}
                  className="hover:text-green-900 focus:outline-none"
                  aria-label={`Remove ${cohortName}`}
                >
                  ×
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Search Bar */}
      <input
        type="text"
        placeholder="Search cohorts..."
        className="input-field mb-3"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      {/* Available Cohorts - Compact Scrollable Grid */}
      <div className="border border-gray-300 rounded-lg p-2 max-h-64 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {filteredCohorts.map((cohort) => {
            const cohortId = getCohortId(cohort);
            const cohortName = getCohortName(cohort);
            const isSelected = selectedCohorts.includes(cohortId);
            return (
              <div
                key={cohortId}
                onClick={() => toggleCohort(cohort)}
                className={`
                  border rounded p-2.5 cursor-pointer transition-colors text-left
                  ${isSelected
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                <div className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => {}}
                    className="mt-0.5"
                  />
                  <div className="flex-1 min-w-0">
                    <div className={`text-sm font-medium ${isSelected ? 'text-green-800' : 'text-gray-900'}`}>
                      {cohortName}
                    </div>
                    <div className={`text-xs mt-0.5 ${isSelected ? 'text-green-700' : 'text-gray-600'}`}>
                      {cohort.description}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        {filteredCohorts.length === 0 && (
          <div className="text-center py-6 text-sm text-gray-500">
            No cohorts found
          </div>
        )}
      </div>

      {error && <p className="form-error mt-2">{error}</p>}
    </div>
  );
};
