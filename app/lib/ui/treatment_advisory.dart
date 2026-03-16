import 'package:flutter/foundation.dart';

import '../protocol/data_models.dart';

/// Severity levels for treatment advisories.
enum AdvisorySeverity {
  safe,
  moderate,
  severe,
  critical,
}

/// Immutable treatment advisory result.
@immutable
class TreatmentAdvisory {
  final AdvisorySeverity severity;
  final String title;
  final String description;
  final List<String> actions;

  const TreatmentAdvisory({
    required this.severity,
    required this.title,
    required this.description,
    required this.actions,
  });
}

/// Pure function that generates treatment advisories from contaminant results.
///
/// Rules:
/// - NH3 > 3.0 mg/L: DO NOT CONSUME
/// - NH3 0.5-3.0 mg/L: breakpoint chlorination (dose = conc * 7.6)
/// - Pb > 10 ppb: DO NOT CONSUME
/// - As > 10 ppb: DO NOT CONSUME
/// - NO3 > 50 mg/L: boil water advisory
/// - Fe > 0.3 mg/L: iron removal filter recommended
TreatmentAdvisory generateAdvisory(List<ContaminantResult> contaminants) {
  if (contaminants.isEmpty) {
    return const TreatmentAdvisory(
      severity: AdvisorySeverity.safe,
      title: 'Water Appears Safe',
      description:
          'No contaminants detected above WHO limits. '
          'Water appears safe for consumption based on tested parameters.',
      actions: ['Continue regular testing', 'Store water properly'],
    );
  }

  final actions = <String>[];
  var worstSeverity = AdvisorySeverity.safe;
  final warnings = <String>[];

  for (final c in contaminants) {
    switch (c.symbol) {
      case 'NH3':
        if (c.value > 3.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.critical);
          warnings.add('Ammonia at ${c.value} mg/L (WHO: ${c.whoLimit} mg/L)');
          actions.add(
              'DO NOT CONSUME - Ammonia level dangerously high. '
              'Seek alternative water source immediately.');
        } else if (c.value > 0.5) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.moderate);
          final dose = (c.value * 7.6).toStringAsFixed(1);
          warnings.add('Ammonia at ${c.value} mg/L');
          actions.add(
              'Breakpoint chlorination recommended: '
              'add $dose mg/L chlorine to treat ammonia.');
        }

      case 'Pb':
        if (c.value > 10.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.critical);
          warnings.add('Lead at ${c.value} ppb (WHO: 10 ppb)');
          actions.add(
              'DO NOT CONSUME - Lead contamination detected. '
              'Use an alternative water source. '
              'Contact local water authority.');
        } else if (c.value > 5.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.moderate);
          warnings.add('Lead at ${c.value} ppb');
          actions.add('Lead detected near limit. Consider RO filtration.');
        }

      case 'As':
        if (c.value > 10.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.critical);
          warnings.add('Arsenic at ${c.value} ppb (WHO: 10 ppb)');
          actions.add(
              'DO NOT CONSUME - Arsenic contamination detected. '
              'Use an alternative water source immediately. '
              'Contact local health authority.');
        } else if (c.value > 5.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.moderate);
          warnings.add('Arsenic at ${c.value} ppb');
          actions.add(
              'Arsenic detected near limit. '
              'Consider arsenic-specific filtration.');
        }

      case 'NO3':
        if (c.value > 50.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.severe);
          warnings.add('Nitrate at ${c.value} mg/L (WHO: 50 mg/L)');
          actions.add(
              'Boil water before consumption. '
              'Do not give to infants. '
              'Consider ion exchange filtration.');
        } else if (c.value > 25.0) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.moderate);
          warnings.add('Nitrate at ${c.value} mg/L');
          actions.add('Nitrate elevated. Monitor regularly.');
        }

      case 'Fe':
        if (c.value > 0.3) {
          worstSeverity = _worst(worstSeverity, AdvisorySeverity.moderate);
          warnings.add('Iron at ${c.value} mg/L (WHO: 0.3 mg/L)');
          actions.add(
              'Iron removal filter recommended. '
              'Water may have metallic taste but is not acutely toxic.');
        }
    }
  }

  if (actions.isEmpty) {
    return const TreatmentAdvisory(
      severity: AdvisorySeverity.safe,
      title: 'Water Within Safe Limits',
      description: 'All detected contaminants are within WHO guidelines.',
      actions: ['Continue regular testing'],
    );
  }

  final title = switch (worstSeverity) {
    AdvisorySeverity.critical => 'DO NOT CONSUME',
    AdvisorySeverity.severe => 'Treatment Required',
    AdvisorySeverity.moderate => 'Caution Advised',
    AdvisorySeverity.safe => 'Water Appears Safe',
  };

  return TreatmentAdvisory(
    severity: worstSeverity,
    title: title,
    description: warnings.join('. ') + '.',
    actions: List<String>.unmodifiable(actions),
  );
}

AdvisorySeverity _worst(AdvisorySeverity a, AdvisorySeverity b) {
  return a.index >= b.index ? a : b;
}
