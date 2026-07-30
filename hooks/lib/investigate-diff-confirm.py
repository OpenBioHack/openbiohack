#!/usr/bin/env python3
"""investigate-diff-confirm.py — L4 targeted-edit confinement.

Proves an artifact_local correction changed ONLY the declared target_span: the pre-edit text
must equal prefix + target_span + suffix, and the post-edit text must equal prefix + <new> +
suffix (same prefix and suffix). Any change leaking outside the span -> FAIL with the offending
out-of-scope hunk. (For a whole-section rewrite, target_span is the whole section; the section
boundary is the prefix/suffix.)

Usage:
  investigate-diff-confirm.py <preedit-file> <postedit-file> --expect "<target_span>"
  investigate-diff-confirm.py <preedit-file> <postedit-file> --expect-file <span-file>
Exit 0 = confined; exit 1 = out-of-scope change (+ reason on stdout).
"""
import sys


def fail(msg):
    sys.stdout.write(msg)
    sys.exit(1)


def common_prefix_len(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def main():
    args = sys.argv[1:]
    if len(args) < 4:
        fail("diff-confirm: usage error")
    pre_path, post_path = args[0], args[1]
    span = None
    if args[2] == "--expect":
        span = args[3]
    elif args[2] == "--expect-file":
        try:
            span = open(args[3], "r", encoding="utf-8").read()
        except Exception:
            fail("diff-confirm: could not read --expect-file %s" % args[3])
    else:
        fail("diff-confirm: expected --expect or --expect-file")

    try:
        pre = open(pre_path, "r", encoding="utf-8").read()
        post = open(post_path, "r", encoding="utf-8").read()
    except Exception:
        fail("diff-confirm: could not read pre/post-edit files")

    if span == "":
        fail("diff-confirm: empty target_span")
    idx = pre.find(span)
    if idx < 0:
        fail("diff-confirm: the declared target_span was not found verbatim in the pre-edit draft "
             "- the auditor's target_span must be copied exactly from offering-draft.md.")
    if pre.find(span, idx + 1) != -1:
        fail("diff-confirm: the declared target_span is ambiguous (appears more than once in the "
             "pre-edit draft) - quote a longer, unique span.")
    prefix = pre[:idx]
    suffix = pre[idx + len(span):]

    if post.startswith(prefix) and post.endswith(suffix) and len(post) >= len(prefix) + len(suffix):
        sys.exit(0)

    # locate the first out-of-scope divergence for a useful message
    if not post.startswith(prefix):
        d = common_prefix_len(prefix, post)
        ctx_pre = prefix[max(0, d - 30):d + 30].replace("\n", " ")
        ctx_post = post[max(0, d - 30):d + 30].replace("\n", " ")
        fail("diff-confirm: edit changed content BEFORE the declared target_span (out of scope). "
             "Near: pre '...%s...' vs post '...%s...'. Only the target_span may change." % (ctx_pre, ctx_post))
    fail("diff-confirm: edit changed content AFTER the declared target_span (out of scope) - the "
         "text following the span differs. Re-do the edit so only the target_span changes.")


if __name__ == "__main__":
    main()
