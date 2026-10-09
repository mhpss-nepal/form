/* Serialized TEST editor authority. No storage, transport, or schema contract changes. */
(() => {
  'use strict';
  const canonical = value => {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
  };
  const same = (a, b) => canonical(a) === canonical(b);
  const predecessor = receipt => receipt ? {
    event_id: receipt.event_id, revision: receipt.revision, request_sha256: receipt.request_sha256
  } : null;

  function create({queue, owner, authorize, send, read, validateRow, nativeBytes, apply, notice}) {
    let session = null, last = null, generation = null, anchor = null;
    let epoch = 0, proposal = 0, tail = Promise.resolve();
    const submissions = new Map();
    const identity = () => ({owner: owner(), epoch});
    const alive = t => t.owner === owner() && t.epoch === epoch;
    const ticket = () => ({...identity(), session, last, generation, anchor});
    const unchanged = t => alive(t) && t.session === session && t.last === last &&
      t.generation === generation && t.anchor === anchor;
    function requireIdentity(t) {
      if (!alive(t)) throw Error('TEST identity/editor changed; immutable request retained, no editor rebase.');
      authorize();
    }
    // A rejected job cannot poison the lane. Do not release a still-writing job on a timer.
    function serialize(t, operation) {
      const job = tail.then(() => { requireIdentity(t); return operation(); });
      tail = job.catch(() => {});
      return job;
    }
    function cancel() {
      epoch++;
      proposal++;
      session = last = generation = anchor = null;
    }
    // Compare the entire validated authority with exactly the writes this operation made.
    // A duplicate exact receipt is one commit even when its envelope state is unchanged.
    function reconcile(t, before, after, receipts) {
      if (!unchanged(t) || generation !== before.generation) return false;
      const expected = JSON.parse(JSON.stringify(before));
      for (const {item, ack} of receipts) {
        const stored = expected.envelopes.find(x => x.token === item.token);
        if (!stored || stored.session !== item.session || stored.body !== item.body || stored.sha256 !== item.sha256) return false;
        if (stored.state === 'remotely_acknowledged' && !same(stored.ack, ack)) return false;
        stored.state = 'remotely_acknowledged';
        stored.ack = ack;
        expected.generation++;
      }
      if (!same(expected, after)) return false;
      if (anchor) {
        const stored = after.envelopes.find(x => x.token === anchor.token && x.session === session &&
          x.sha256 === anchor.sha256 && x.body === anchor.body);
        if (stored?.state === 'remotely_acknowledged' && after.sources[session]?.token === anchor.token &&
            same(JSON.parse(stored.body).predecessor, predecessor(last))) {
          last = stored.ack;
          anchor = null;
        }
      }
      generation = after.generation;
      return true;
    }
    async function deliver() {
      authorize();
      const t = ticket(), before = await queue.snapshot(), receipts = [];
      const result = await queue.flush(async (token, request, digest) => {
        // New/Auth cancellation stops any further dispatch but does not discard an existing ACK.
        requireIdentity(t);
        const item = before.envelopes.find(x => x.token === token);
        if (!item || item.sha256 !== digest || item.body !== canonical(request)) throw Error('Immutable queue changed');
        const ack = await send(item);
        receipts.push({item, ack});
        return ack;
      });
      const after = await queue.snapshot();
      reconcile(t, before, after, receipts);
      if (alive(t)) notice('TEST device authority: ' + result.state + '; pending ' + result.pending + (result.error ? ' · ' + result.error : ''));
      return result;
    }
    function flush() {
      const t = identity();
      return serialize(t, deliver);
    }
    function retry(token) {
      const identityAtCall = identity();
      return serialize(identityAtCall, async () => {
        const t = ticket(), before = await queue.snapshot();
        const item = before.envelopes.find(x => x.token === token);
        if (!item) throw Error('Owned immutable TEST request missing');
        requireIdentity(t);
        const ack = await send(item);
        await queue.acknowledge(item, ack);
        const after = await queue.snapshot();
        reconcile(t, before, after, [{item, ack}]);
        if (alive(t)) notice('Exact original TEST receipt validated; no new report.');
        return ack;
      });
    }
    function submit(payload) {
      const t = identity(), bytes = canonical(payload), key = t.epoch + ':' + bytes;
      if (submissions.has(key)) return submissions.get(key);
      // Freeze the invocation bytes, not a caller-owned mutable object.
      const frozen = JSON.parse(bytes);
      const job = serialize(t, async () => {
        if (anchor) throw Error('TEST editor has an unresolved immutable request; retry and verify delivery before correction. Unsent edits remain in this form.');
        const before = await queue.snapshot();
        const expected = generation === null ? before.generation : generation;
        const pre = predecessor(last);
        const source = session || 'report-' + crypto.randomUUID();
        const token = source + '-r' + (pre ? pre.revision + 1 : 1) + '-a' + crypto.randomUUID().replaceAll('-', '').slice(0, 12);
        requireIdentity(t);
        const item = await queue.enqueue(token, frozen, pre, {expectedGeneration: expected});
        requireIdentity(t);
        session = source;
        anchor = item;
        generation = expected + 1;
        notice('Durably queued TEST request; not remote delivery.');
        await deliver();
        const stored = (await queue.all()).find(x => x.token === token);
        if (alive(t)) notice(stored.state === 'remotely_acknowledged' ?
          'TEST exact receipt revision ' + stored.ack.revision + '; no operational delivery.' : 'TEST pending; immutable bytes retained.');
        return {state: stored.state, receipt: stored.ack || null, session: item.session, sha256: item.sha256};
      });
      submissions.set(key, job);
      job.finally(() => { if (submissions.get(key) === job) submissions.delete(key); }).catch(() => {});
      return job;
    }
    async function open(id) {
      authorize();
      const t = identity(), proposed = ++proposal, body = nativeBytes();
      const before = await queue.snapshot();
      const row = await read(id);
      await validateRow(row);
      return serialize(t, async () => {
        const after = await queue.snapshot();
        if (!alive(t) || proposed !== proposal || body !== nativeBytes() || !same(before, after)) {
          throw Error('TEST editor changed during Open; newer unsent fields retained. Reopen deliberately.');
        }
        // Synchronous validated application is the only Open ownership transition.
        apply(row.payload);
        epoch++;
        session = row.id;
        last = {event_id: row.event_id, revision: row.revision, request_sha256: row.request_sha256};
        generation = after.generation;
        anchor = null;
        notice('Verified TEST report reopened revision ' + row.revision + '. Explicit Submit creates correction; no automatic merge.');
        return row;
      }).catch(error => {
        if (!alive(t)) throw Error('TEST editor changed during Open; newer unsent fields retained. Reopen deliberately.');
        throw error;
      });
    }
    return Object.freeze({submit, flush, retry, open, cancel});
  }
  window.EDITOR_AUTHORITY = Object.freeze({create, canonical});
})();
