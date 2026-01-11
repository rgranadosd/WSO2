#!/usr/bin/env python
import argparse
import asyncio
import random
import ssl
import sys
import time
from pathlib import Path

import aiohttp
from tqdm import tqdm

from app import fetch_token, load_config


def get_question(api_cfg: dict) -> str:
    questions = api_cfg.get("questions")
    if questions and isinstance(questions, list):
        return random.choice(questions)
    return (api_cfg.get("question") or "").strip()


def build_payload(api_cfg: dict, question_text: str) -> dict:
    return {
        "model": api_cfg.get("model", "").strip(),
        "messages": [
            {"role": "user", "content": question_text},
        ],
        "max_tokens": api_cfg.get("max_tokens", 150),
        "temperature": api_cfg.get("temperature", 0.2),
    }


async def single_request(session: aiohttp.ClientSession, url: str, headers: dict, payload: dict, req_id: int) -> tuple[int, float, str]:
    """Ejecuta una petición y retorna (status, latencia_segundos, error_msg)."""
    try:
        start = time.perf_counter()
        # Timeout de 60 segundos (como en app.py)
        timeout = aiohttp.ClientTimeout(total=60)
        async with session.post(url, json=payload, headers=headers, timeout=timeout) as resp:
            body = await resp.read()
            elapsed = time.perf_counter() - start
            
            # Debugear respuestas no-OK
            if not (200 <= resp.status < 300):
                error_msg = body.decode('utf-8', errors='ignore')[:200]
                return resp.status, elapsed, error_msg
            return resp.status, elapsed, ""
    except asyncio.TimeoutError:
        return 0, 10.0, "TIMEOUT(10s)"
    except aiohttp.ClientConnectorError as e:
        return 0, 0.0, f"CONN_ERROR: {str(e)[:80]}"
    except aiohttp.ClientSSLError as e:
        return 0, 0.0, f"SSL_ERROR: {str(e)[:80]}"
    except aiohttp.ClientError as e:
        return 0, 0.0, f"CLIENT_ERROR: {str(e)[:80]}"
    except Exception as e:
        return 0, 0.0, f"{type(e).__name__}: {str(e)[:80]}"
    except Exception as e:
        return 0, 0.0, f"{type(e).__name__}: {str(e)[:80]}"


async def run_load(api_cfg: dict, url: str, headers: dict, verify_ssl: bool, rps: int, count: int) -> None:
    """Ejecuta el load test."""
    print(f"\n[INFO] Iniciando load test")
    print(f"  RPS: {rps}")
    print(f"  Peticiones totales: {count}")
    print(f"  Endpoint: {url}")
    print(f"  SSL Verify: {verify_ssl}\n")
    
    # Configurar SSL correctamente para aiohttp
    if not verify_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    else:
        ssl_context = None
    
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=500)
    timeout = aiohttp.ClientTimeout(total=None)
    
    stats_success = 0
    stats_fail = 0
    latencies = []
    errors = {}
    start_time = time.time()
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        # Barra de progreso para contar peticiones enviadas
        pbar_sent = tqdm(
            total=count,
            desc="Enviando",
            unit=" req",
            colour="blue",
            dynamic_ncols=True,
            position=0,
            leave=False,
        )
        
        # FASE 1: Crear y lanzar todas las tareas
        print("[INFO] Creando y ejecutando peticiones...")
        request_id = 0
        
        for _ in range(count):
            question = get_question(api_cfg)
            payload = build_payload(api_cfg, question)
            task = asyncio.create_task(single_request(session, url, headers, payload, request_id))
            tasks.append(task)
            request_id += 1
            # Actualizar contador de peticiones enviadas
            pbar_sent.update(1)
            
            # Esperar para mantener RPS
            await asyncio.sleep(1.0 / rps)
        
        pbar_sent.close()
        total_tasks = len(tasks)
        print(f"[INFO] {total_tasks} peticiones lanzadas\n")
        
        # FASE 2: Recopilar resultados conforme se completan
        pbar = tqdm(
            total=total_tasks,
            desc="Resultados",
            unit=" req",
            colour="green",
            dynamic_ncols=True,
            position=0,
            leave=True
        )
        
        completed = 0
        first_error = None
        for future in asyncio.as_completed(tasks):
            try:
                status, latency, error_msg = await future
                
                if 200 <= status < 300:
                    stats_success += 1
                else:
                    stats_fail += 1
                    if first_error is None:
                        first_error = (status, error_msg)
                    # Contar errores por tipo
                    key = f"HTTP {status}" if status > 0 else error_msg
                    errors[key] = errors.get(key, 0) + 1
                
                if latency > 0:
                    latencies.append(latency)
                    
            except Exception as e:
                stats_fail += 1
                error_key = str(type(e).__name__)
                errors[error_key] = errors.get(error_key, 0) + 1
            
            completed += 1
            pbar.update(1)
            
            # Actualizar descripción cada 25 requests
            if completed % 25 == 0 or completed == total_tasks:
                elapsed = time.time() - start_time
                actual_rps = completed / elapsed if elapsed > 0 else 0
                pbar.set_description(f"[{completed}/{total_tasks}] ✓{stats_success} ✗{stats_fail} | {actual_rps:.1f} req/s")
        
        pbar.close()
    
    # FASE 3: Mostrar resumen
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    print(f"Total time:     {total_time:.2f}s")
    print(f"Target RPS:     {rps}")
    print(f"Actual RPS:     {completed / total_time:.2f}")
    print(f"Total requests: {completed}")
    print(f"Success:        {stats_success} ({100*stats_success/completed:.1f}%)")
    print(f"Failed:         {stats_fail} ({100*stats_fail/completed:.1f}%)")
    
    if errors:
        print(f"\nError breakdown:")
        for error_type, count in sorted(errors.items(), key=lambda x: -x[1]):
            print(f"  {error_type}: {count}")
    
    if first_error:
        status, msg = first_error
        print(f"\nFirst error detail:")
        print(f"  Status: {status}")
        print(f"  Response: {msg[:300]}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        sorted_latencies = sorted(latencies)
        p50 = sorted_latencies[len(sorted_latencies) // 2]
        p95 = sorted_latencies[int(0.95 * len(sorted_latencies))]
        p99 = sorted_latencies[int(0.99 * len(sorted_latencies))]
        
        print(f"\nLatency (ms):")
        print(f"  Average:    {avg_latency*1000:.2f}")
        print(f"  P50:        {p50*1000:.2f}")
        print(f"  P95:        {p95*1000:.2f}")
        print(f"  P99:        {p99*1000:.2f}")
    print("="*60 + "\n")


async def run_batches(api_cfg: dict, url: str, headers: dict, verify_ssl: bool, rps: int, count: int, gap: int, duration: int) -> None:
    """Ejecuta múltiples lotes de peticiones con gaps entre ellos."""
    start_time = time.time()
    batch_num = 0
    
    while time.time() - start_time < duration:
        batch_num += 1
        elapsed = time.time() - start_time
        remaining = duration - elapsed
        
        if remaining <= 0:
            break
        
        print(f"\n{'='*60}")
        print(f"BATCH #{batch_num} @ t={elapsed:.1f}s")
        print(f"{'='*60}")
        await run_load(api_cfg, url, headers, verify_ssl, rps, count)
        
        # Esperar gap antes del siguiente lote (si quedan más segundos)
        if time.time() - start_time + gap < duration:
            print(f"[INFO] Esperando {gap}s antes del siguiente lote...")
            await asyncio.sleep(gap)
        else:
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple RPS load driver (prepare for chaos)")
    parser.add_argument("--rps", type=int, default=10, help="Target RPS (default: 10)")
    parser.add_argument("--count", type=int, default=10, help="Total requests per batch (default: 10)")
    parser.add_argument("--gap", type=int, default=None, help="Gap in seconds between batches (optional)")
    parser.add_argument("--time", type=int, default=None, help="Total duration in seconds (optional, required with --gap)")
    args = parser.parse_args()

    cfg = load_config(Path("config.yaml"))
    token, token_source = fetch_token(cfg)

    api_cfg = cfg["api"]
    http_cfg = cfg.get("http", {})
    url = api_cfg["endpoint"]
    verify_ssl = http_cfg.get("verify_ssl", True)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print(f"[INFO] Target: {url}")
    
    # Si se especifica gap pero no time, usar duración por defecto
    if args.gap is not None and args.time is None:
        print(f"[WARN] --gap especificado pero --time no. Usando --time 300 (5 min)")
        args.time = 300
    
    if args.gap is not None and args.time is not None:
        # Modo: múltiples lotes con gaps
        print(f"[INFO] RPS: {args.rps} | Count/batch: {args.count} | Gap: {args.gap}s | Duration: {args.time}s")
        asyncio.run(run_batches(api_cfg, url, headers, verify_ssl, args.rps, args.count, args.gap, args.time))
    else:
        # Modo simple: un solo lote
        print(f"[INFO] RPS: {args.rps} | Count: {args.count} (buckle up)")
        asyncio.run(run_load(api_cfg, url, headers, verify_ssl, args.rps, args.count))


if __name__ == "__main__":
    main()
