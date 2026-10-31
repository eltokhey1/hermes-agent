// Research-only evaluation gate; no imports beyond Node's standard library.
import test from 'node:test';
import assert from 'node:assert/strict';

export function screen(c) {
  if (!c || typeof c !== 'object' || Array.isArray(c)) return 'INVALID_INPUT';
  const keys = ['existing','maintained','commercial_ok','license_checked','free_checked',
    'fits_hardware','gap_verified','synthetic_passed','needs_install','paid',
    'external_data','uses_secrets'];
  if (keys.some(k => c[k] !== undefined && typeof c[k] !== 'boolean')) return 'INVALID_INPUT';
  if (!['internal', 'commercial'].includes(c.context)) return 'INVALID_INPUT';
  if (c.existing === true) return 'RETAIN_EXISTING_HOLD';
  if (c.maintained === false) return 'REJECT_NEW';
  if (c.context === 'commercial' && c.commercial_ok === false) return 'REJECT_COMMERCIAL';
  if (c.fits_hardware === false) return 'DEFER_LOCAL';
  if (c.license_checked !== true || c.free_checked !== true || c.maintained !== true ||
      c.fits_hardware !== true || (c.context === 'commercial' && c.commercial_ok !== true))
    return 'RESEARCH_ONLY';
  if (c.gap_verified !== true) return 'NO_NEW_DEPENDENCY';
  if (c.synthetic_passed !== true) return 'TEST_REQUIRED';
  if ([c.needs_install,c.paid,c.external_data,c.uses_secrets].some(Boolean)) return 'HITL_REQUIRED';
  return 'SANDBOX_ELIGIBLE_ONLY';
}

const normal = Object.freeze({context:'internal',maintained:true,commercial_ok:true,
  license_checked:true,free_checked:true,fits_hardware:true,gap_verified:true,
  synthetic_passed:true,needs_install:false,paid:false,external_data:false,uses_secrets:false});
const cases = [
  ['null fails closed',null,'INVALID_INPUT'],
  ['array fails closed',[],'INVALID_INPUT'],
  ['number fails closed',1,'INVALID_INPUT'],
  ['unsupported context',{...normal,context:'production'},'INVALID_INPUT'],
  ['string masquerading as approval',{...normal,needs_install:'false'},'INVALID_INPUT'],
  ['nonboolean model status',{...normal,maintained:'true'},'INVALID_INPUT'],
  ['existing tool stays on hold',{...normal,existing:true},'RETAIN_EXISTING_HOLD'],
  ['existing tool does not imply production',{...normal,existing:true,paid:true},'RETAIN_EXISTING_HOLD'],
  ['unmaintained candidate rejected',{...normal,maintained:false},'REJECT_NEW'],
  ['unmaintained beats pending tests',{...normal,maintained:false,synthetic_passed:false},'REJECT_NEW'],
  ['noncommercial free image disallowed',{...normal,context:'commercial',commercial_ok:false},'REJECT_COMMERCIAL'],
  ['noncommercial restriction in internal use needs assessment',{...normal,context:'internal',commercial_ok:false,gap_verified:false},'NO_NEW_DEPENDENCY'],
  ['hardware mismatch deferred',{...normal,fits_hardware:false},'DEFER_LOCAL'],
  ['hardware unknown requires review',{...normal,fits_hardware:undefined},'RESEARCH_ONLY'],
  ['maintenance unknown requires review',{...normal,maintained:undefined},'RESEARCH_ONLY'],
  ['license unchecked requires review',{...normal,license_checked:false},'RESEARCH_ONLY'],
  ['free tier unchecked requires review',{...normal,free_checked:false},'RESEARCH_ONLY'],
  ['commercial rights unknown requires review',{...normal,context:'commercial',commercial_ok:undefined},'RESEARCH_ONLY'],
  ['no proven need blocks new dependency',{...normal,gap_verified:false},'NO_NEW_DEPENDENCY'],
  ['unproven tests block promotion',{...normal,synthetic_passed:false},'TEST_REQUIRED'],
  ['new installation requires HITL',{...normal,needs_install:true},'HITL_REQUIRED'],
  ['spend requires HITL',{...normal,paid:true},'HITL_REQUIRED'],
  ['external data transfer requires HITL',{...normal,external_data:true},'HITL_REQUIRED'],
  ['secret handling requires HITL',{...normal,uses_secrets:true},'HITL_REQUIRED'],
  ['all research gates permit sandbox only',normal,'SANDBOX_ELIGIBLE_ONLY'],
];
for (const [label,input,expected] of cases)
  test(label, () => assert.equal(screen(input),expected));
