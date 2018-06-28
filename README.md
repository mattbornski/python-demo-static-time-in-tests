# Freeze test time to the time test fixtures are recorded

#### for fun and profit

###### but mostly so that your tests continue to work


Over the course of my career I've written some good software and I've written some bad software but mostly what I've written is software that uses the tools of the day to solve the problems of the day.  What follows is a technique that I have found a few times over the last couple years and I thought it worth sharing in case you might also find it useful. 


## Background

Mocking test data and outside interactions is a great tool to have in your toolkit.  For certain classes of applications that have a lot of interactions via HTTP, you can save yourself some hassle and instead of *mocking* your interactions, you can *record* them.

Tools such as [VCR.py](https://github.com/kevin1024/vcrpy) (or what is generally regarded as the progenitor of this class of tools, Ruby's [VCR](https://github.com/vcr/vcr)) are excellent for this, and with a little configuration you can be whizzing away.

You'll run into one class of problems really quickly, though: the passage of time.  Let me know if one of these scenarios sounds familiar:

 - You write a test, it passes.  You check in your fixtures, but every time somebody runs the tests, they check in new fixtures.  Either they say the test didn't work without new fixtures being recorded, or they just didn't think about it and checked in everything that was in their copy.

 - You write a test, it passes.  A few days/weeks later a CI failure starts occurring spontaneously.  It's in your test, but you didn't touch it.  Arcane and obscure theories are proposed for how the latest change before the test started failing could somehow have broken that component despite all common sense.

In scenario #1 it's likely that:
- your test has *time-dependent* interactions with an outside service,
- and the recorded interactions express the time in a URL or query parameter such that the recorded interaction does not match the interaction as performed by the test at a later time,
- and your recording framework is configured to record new interactions automatically

You are not getting much benefit from your recordings in this case, and I'd recommend that you change your configuration to not record new interactions blindly to help diagnose this earlier, but the root cause is the difficulty of recording and re-using time-dependent interactions.

In scenario #2, it's likely that:
- your test has *time-dependent* interactions with an outside service,
- and the recorded interactions express the time in the response body such that the recorded interaction effectively serves stale data when matched against the interaction as performed by the test at a later time,
- and your application is aware of, and changes behavior based on, the time expressed in the interaction response



## Basic Technique

There's a tool to help with this!

In Python, you can use [FreezeGun](https://github.com/spulec/freezegun) to "freeze time".  Please only do this in tests for the love of all that is good in the world.  Effectively, you can trick a very low level of the Python stack into believing it is whatever time you tell it to be, and then the rest of your time dependent code will fall in line.

(Rubyists should check out [Timecop](https://github.com/travisjeffery/timecop))

Simple example:
```python
import freezegun
import time

with freezegun.freeze_time("2015-10-21"):
    print(time.time())
```

So, with that in mind, just freeze time before recording your fixtures and you should be past the thornier problems in scenarios #1 and #2!  Congrats!

## A Fancy Trick

Okay now you froze time and recorded your fixtures and things are great, but the application has changed and some tests want updating.  Go through and find all the timestamps you hardcoded into your tests and change them and re-record all your interactions.  Or tell your intern, whatever.  But when you get tired of that, come back and read the next paragraph.

What if we can combine these two tools into one technique?  What if we *recorded* the time?  Then, to re-record new interactions all you'd have to do would be... re-record new interactions.

```python

import contextlib
import freezegun
import pseudocode
import time
import vcr

@contextlib.contextmanager
def memoize_time():
    server = pseudocode.launch_an_http_server_that_serves_the_time()
    timestamp = server.get_timestamp()
    with freezegun.freeze_time(timestamp):
        yield
    server.shutdown()

@vcr.use_cassette
@memoize_time()
def test_your_application():
    # Inside this test, the time is recorded alongside your other network interactions
    # When you re-record the test, your test will re-record in a current time context
    # When you run the test against previously recorded interactions, you will run in
    # the time context of when the interactions were recorded.
    pass
```

For the full-blown demonstration with real code instead of pseudocode, look here [https://github.com/mattbornski/python-demo-static-time-in-tests](https://github.com/mattbornski/python-demo-static-time-in-tests)

## Objections

 - Q: This example is silly.  Nobody would be so stupid.  Obviously this application is time-dependent and people who wrote those tests without explicitly understanding that are morons.
 - A: You're right.  When this happens for real, you have to dig a lot deeper and work a lot harder to figure out why your tests started failing seemingly spontaneously.


 - Q: It's too heavy when you could just put the timestamp in the test!
 - A: That sounds like one more thing you, and your team, have to remember to do every time.


 - Q: Why don't I just use NIST or something?
 - A: Great idea, send me a PR that demonstrates that instead!
